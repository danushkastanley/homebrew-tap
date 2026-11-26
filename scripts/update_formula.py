#!/usr/bin/env python3
"""Write Formula/kubectl-memlens.rb for a KubeMemLens stable release.

usage: update_formula.py [--check]

Without --check it renders the formula for the latest stable release.
With --check it renders for the version already in the formula and fails if
the result differs from the committed file.

The hashes are trusted only through the release's signatures: cosign must
verify promotion-checksums.txt against the promotion workflow of that tag, and
that file must cover checksums.txt, which lists the archives. Needs cosign.
"""
import hashlib
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPOSITORY = "https://github.com/danushkastanley/KubeMemLens"
ISSUER = "https://token.actions.githubusercontent.com"
FORMULA = Path(__file__).resolve().parent.parent / "Formula" / "kubectl-memlens.rb"
STABLE_TAG = re.compile(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
PLATFORMS = ("darwin_arm64", "darwin_amd64", "linux_arm64", "linux_amd64")

TEMPLATE = '''# Written by scripts/update_formula.py from the signed checksums of a
# KubeMemLens release. Change the script, not this file.
class KubectlMemlens < Formula
  desc "Kubectl plugin that explains why Pod memory is high"
  homepage "{repository}"
  license "Apache-2.0"

  on_macos do
    on_arm do
      url "{url_darwin_arm64}"
      sha256 "{sha_darwin_arm64}"
    end
    on_intel do
      url "{url_darwin_amd64}"
      sha256 "{sha_darwin_amd64}"
    end
  end

  on_linux do
    on_arm do
      url "{url_linux_arm64}"
      sha256 "{sha_linux_arm64}"
    end
    on_intel do
      url "{url_linux_amd64}"
      sha256 "{sha_linux_amd64}"
    end
  end

  def install
    bin.install "kubectl-memlens"
  end

  def caveats
    <<~EOS
      Run the plugin as "kubectl memlens".
      Full cgroup detail needs the KubeMemLens Helm chart in the cluster:
        {repository}/blob/main/docs/installation.md
      Without it, the plugin shows Metrics API working set only, which needs
      metrics-server.
    EOS
  end

  test do
    assert_match "version=v#{{version}}", shell_output("#{{bin}}/kubectl-memlens version")
  end
end
'''


def fail(message):
    raise SystemExit(f"update_formula: {message}")


def latest_stable_tag():
    # The releases/latest page redirects to the newest release that is neither
    # a draft nor a prerelease.
    with urllib.request.urlopen(f"{REPOSITORY}/releases/latest", timeout=60) as response:
        tag = response.geturl().rsplit("/", 1)[-1]
    if not STABLE_TAG.fullmatch(tag):
        fail(f"the latest release is {tag!r}, not a stable vX.Y.Z tag")
    return tag


def committed_tag():
    # Homebrew reads the version from the archive address, so the formula has
    # no version line of its own.
    tags = set(re.findall(r"/releases/download/([^/]+)/", FORMULA.read_text()))
    if len(tags) != 1 or not STABLE_TAG.fullmatch(min(tags)):
        fail(f"{FORMULA} does not name exactly one stable release: {sorted(tags)}")
    return min(tags)


def download(tag, name, directory):
    target = directory / name
    with urllib.request.urlopen(f"{REPOSITORY}/releases/download/{tag}/{name}", timeout=300) as response:
        target.write_bytes(response.read())
    return target


def listed(checksum_file):
    return dict(reversed(line.split()) for line in checksum_file.read_text().splitlines() if line.strip())


def signed_checksums(tag):
    """Return {archive name: sha256} for tag, or stop if a signature does not hold."""
    with tempfile.TemporaryDirectory() as work:
        work = Path(work)
        record = download(tag, "promotion-checksums.txt", work)
        bundle = download(tag, "promotion-checksums.sigstore.json", work)
        checksums = download(tag, "checksums.txt", work)
        identity = f"{REPOSITORY}/.github/workflows/promote.yml@refs/tags/{tag}"
        verified = subprocess.run(
            ["cosign", "verify-blob", "--bundle", str(bundle), "--certificate-identity", identity,
             "--certificate-oidc-issuer", ISSUER, str(record)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False)
        if verified.returncode != 0:
            fail(f"promotion-checksums.txt is not signed by the {tag} promotion workflow: {verified.stderr.strip()}")
        if listed(record).get("checksums.txt") != hashlib.sha256(checksums.read_bytes()).hexdigest():
            fail(f"checksums.txt of {tag} differs from the signed promotion record")
        return listed(checksums)


def render(tag):
    version = tag[1:]
    checksums = signed_checksums(tag)
    values = {"repository": REPOSITORY}
    for platform in PLATFORMS:
        name = f"kube-memlens_{version}_{platform}.tar.gz"
        if name not in checksums:
            fail(f"the signed checksums of {tag} do not list {name}")
        values[f"url_{platform}"] = f"{REPOSITORY}/releases/download/{tag}/{name}"
        values[f"sha_{platform}"] = checksums[name]
    return TEMPLATE.format(**values)


def main(arguments):
    if arguments not in ([], ["--check"]):
        fail(__doc__.strip().splitlines()[2])
    if arguments:
        tag = committed_tag()
        if render(tag) != FORMULA.read_text():
            fail(f"{FORMULA.name} differs from the formula rendered from the signed {tag} checksums; "
                 "run scripts/update_formula.py, or change the template in it")
        print(f"{FORMULA.name} matches the signed {tag} release")
        return
    tag = latest_stable_tag()
    FORMULA.write_text(render(tag))
    print(f"wrote {FORMULA.name} for {tag}")


if __name__ == "__main__":
    main(sys.argv[1:])
