# Homebrew tap for KubeMemLens

[![Tests](https://github.com/danushkastanley/homebrew-tap/actions/workflows/tests.yml/badge.svg)](https://github.com/danushkastanley/homebrew-tap/actions/workflows/tests.yml) [![Update formula](https://github.com/danushkastanley/homebrew-tap/actions/workflows/update.yml/badge.svg)](https://github.com/danushkastanley/homebrew-tap/actions/workflows/update.yml)

A [Homebrew](https://brew.sh) tap for the `kubectl memlens` plugin from
[KubeMemLens](https://github.com/danushkastanley/KubeMemLens). The plugin
explains why Pod memory is high, using cgroup v2 evidence.

## Install

```sh
brew install danushkastanley/tap/kubectl-memlens
kubectl memlens version
```

Homebrew puts `kubectl-memlens` on your `PATH`, which is how `kubectl` finds the
plugin. macOS and Linux are supported, on Apple silicon, Intel and 64-bit Arm.
The formula installs the prebuilt binary from the KubeMemLens release; it does
not build from source and does not install `kubectl`.

Full cgroup detail needs the KubeMemLens Helm chart in the cluster; see the
[installation guide](https://github.com/danushkastanley/KubeMemLens/blob/main/docs/installation.md).
Without the chart the plugin shows Metrics API working set only, which needs
metrics-server.

## Update and remove

```sh
brew upgrade kubectl-memlens
brew uninstall kubectl-memlens
```

## How the formula stays current

`Formula/kubectl-memlens.rb` is written by `scripts/update_formula.py`. Do not
edit the formula by hand; change the template in the script.

The script trusts a hash only through the release's signatures. It asks
[cosign](https://docs.sigstore.dev/cosign/) to verify the release's
`promotion-checksums.txt` against the KubeMemLens promotion workflow for that
exact tag, checks that this signed record covers `checksums.txt`, and takes the
four archive hashes from there. If any step fails it writes nothing.

The `Update formula` workflow runs the script every four hours. When KubeMemLens
publishes a new stable release it commits the new formula with this repository's
own workflow token and then starts the `Tests` workflow for it. No other
repository holds a credential for this one.

The `Tests` workflow installs the formula on macOS and Linux runners, runs its
test, and checks that the committed formula is exactly what the script renders
from the signed release.

A formula update is committed before its install tests run. If those tests fail,
the badge above turns red; revert the commit until the release is fixed.

GitHub pauses scheduled workflows in a repository that has had no activity for
60 days. If a release does not arrive here within a few hours, check that
`Update formula` is still enabled on the Actions tab, or run it by hand.

## Report a problem

For a wrong hash or a failed install, open an issue in this repository. For
anything about the plugin itself, use the
[KubeMemLens issues](https://github.com/danushkastanley/KubeMemLens/issues).
