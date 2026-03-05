{ pkgs, ... }: {
  channel = "unstable";
  packages = [
    pkgs.python313
    pkgs.gnupg
    pkgs.openssh
  ];
  env = { };
  idx = {
    extensions = [
      "mhutchie.git-graph"
      "oderwat.indent-rainbow"
      "esbenp.prettier-vscode"
      "google.gemini-cli-vscode-ide-companion"
      "ms-python.python"
      "ms-python.debugpy"
    ];
    previews = {
      enable = false;
    };
    workspace = {
      onCreate = { };
      onStart = { };
    };
  };
}
