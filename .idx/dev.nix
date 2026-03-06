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
      "ms-python.autopep8"
      "GraphQL.vscode-graphql"
      "GraphQL.vscode-graphql-syntax"
    ];
    previews = {
      enable = false;
    };
    workspace = {
      onCreate = {
        create_venv = "python -m venv .venv";
        activate = "source .venv/bin/activate";
        install_prep = "pip install -U pip";
        install_wheel = "pip install wheel";
        install = "pip install -r requirements.txt";
        default.openFiles = [ "fanza/fanza/settings.py" ];
      };
      onStart = { };
    };
  };
}
