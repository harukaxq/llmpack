class Llmpack < Formula
  desc "Tool for combining code files into a single document"
  homepage "https://github.com/halst256/llmpack"
  url "https://github.com/halst256/llmpack/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_AFTER_RELEASE"
  license "MIT"

  depends_on "python@3.12"

  def install
    # Create a virtualenv and install the package
    venv = virtualenv_create(libexec, "python3.12")
    # buildpath はソースコードが展開される一時ディレクトリを指す
    system libexec/"bin/pip", "install", "-v", "--no-deps", buildpath

    # llmpackコマンドへのシンボリックリンクなどをbinに配置
    # write_env_scriptを使うことで、virtualenvのpythonを使うように設定できる
    (bin/"llmpack").write_env_script libexec/"bin/llmpack", PATH: "#{libexec}/bin:$PATH"
  end

  test do
    # Add a test to verify the installation
    system "#{bin}/llmpack", "--help"
  end
end
