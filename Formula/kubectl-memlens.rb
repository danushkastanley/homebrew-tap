# Written by scripts/update_formula.py from the signed checksums of a
# KubeMemLens release. Change the script, not this file.
class KubectlMemlens < Formula
  desc "Kubectl plugin that explains why Pod memory is high"
  homepage "https://github.com/danushkastanley/KubeMemLens"
  license "Apache-2.0"

  on_macos do
    on_arm do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.6/kube-memlens_1.0.6_darwin_arm64.tar.gz"
      sha256 "97283a7031bf96ad559c93c953e4f76ac1a6dbc631ceebb30ca9083b4721393c"
    end
    on_intel do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.6/kube-memlens_1.0.6_darwin_amd64.tar.gz"
      sha256 "732953c0c88a5e6bec151af807ff64d1aee6a31ff5666cc79a7d7c25a460d7a3"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.6/kube-memlens_1.0.6_linux_arm64.tar.gz"
      sha256 "5abf16ff79fc98f6aef9336ac4a85f9f0db4ebc74d0cc0569e393f284fb8934b"
    end
    on_intel do
      url "https://github.com/danushkastanley/KubeMemLens/releases/download/v1.0.6/kube-memlens_1.0.6_linux_amd64.tar.gz"
      sha256 "dc3db8e220130f67dd2ef0c937ec157686b62c09f0aa8cc6925e43672a20fd9f"
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
