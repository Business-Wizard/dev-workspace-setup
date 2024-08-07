let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";
  pkgs = import nixpkgs { config = {allowUnfree=true;}; overlays = []; };
in

let
  shell_packages = with pkgs; [
    nushell
    bat
    eza
    pre-commit
    rye
    cargo
    rustup
    vscode
    docker
      podman
  ];
in

pkgs.mkShell {
  buildInputs = shell_packages;

  shellHook = ''
    if [ ! -d ".venv" ] && [ -f "pyproject.toml" ]; then
      echo "Creating a virtual environment..."
      rye sync
    fi

    if [ -d ".venv" ]; then
      echo "Activating the virtual environment..."
      source .venv/bin/activate
    fi

    nu -c '
      let podman_vm_is_running = (podman machine info | from json | get machinestate) == "Running";
      if not $podman_vm_is_running {
        echo "Starting the podman VM..."
        podman machine start
      }
    '

    nu;
  '';
}
