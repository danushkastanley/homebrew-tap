# Written by scripts/update_formula.py from the signed checksums of a
# KubeMemLens release. Change the script, not this file.
class KubectlMemlens < Formula
  desc "Kubectl plugin that explains why Pod memory is high"
  homepage "https://github.com/danushkastanley/KubeMemLens"
  license "Apache-2.0"

  on_macos do
    on_arm do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.5/kube-memlens_1.0.5_darwin_arm64.tar.gz"
      sha256 "fff17a6875e5d2c32323c84381df7ffa808ab8607bb475cc83466708d855aab6"
    end
    on_intel do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.5/kube-memlens_1.0.5_darwin_amd64.tar.gz"
      sha256 "a0ae93e0de8df0fe32d0c74b0c17d8360783398f70292497a64e88f23f64d13f"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.5/kube-memlens_1.0.5_linux_arm64.tar.gz"
      sha256 "764338f49ef532b9ba295cf00a45695e055915b3f984b257ff18a8e369dbbee5"
    end
    on_intel do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.5/kube-memlens_1.0.5_linux_amd64.tar.gz"
      sha256 "5668718e4dccbdd31b4b2da66805f7ad2344cb587ef9799f53618d2c98936d82"
    end
  end

  def install
    bin.install "kubectl-memlens"
  end

  def caveats
    <<~EOS
      Run the plugin as "kubectl memlens".
      Full cgroup detail needs the KubeMemLens Helm chart in the cluster:
        https://github.com/danushkastanley/KubeMemLens/blob/main/docs/installation.md
      Without it, the plugin shows Metrics API working set only, which needs
      metrics-server.
    EOS
  end

  test do
    assert_match "version=v#{version}", shell_output("#{bin}/kubectl-memlens version")
  end
end
