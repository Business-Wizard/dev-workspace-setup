let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-25.05";
  pkgs = import nixpkgs { config = {allowUnfree=true;}; overlays = []; };
in

let
  shell_packages = with pkgs; [
    bat
    eza
    pre-commit
    uv
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
      uv sync
    fi

    if [ -d ".venv" ]; then
      echo "Activating the virtual environment..."
      source .venv/bin/activate
    fi

    podman_vm_state=$(podman machine info --format json | jq -r '.MachineState')
    if [ "$podman_vm_state" != "Running" ]; then
      echo "Starting the podman VM..."
      podman machine start
    fi
  '';
}
