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
    has_venv_dir=false
    has_pyproject=false
    is_linux=false

    [ -d ".venv" ] && has_venv_dir=true
    [ -f "pyproject.toml" ] && has_pyproject=true
    [ "$(uname -s)" = "Linux" ] && is_linux=true

    if ! $has_venv_dir && $has_pyproject; then
      echo "Creating a virtual environment..."
      uv sync
    fi

    if $has_venv_dir; then
      echo "Activating the virtual environment..."
      source .venv/bin/activate
    fi

    if ! $is_linux; then
      podman_vm_state=$(podman machine info --format json | jq -r '.MachineState')
      podman_vm_running=false
      [ "$podman_vm_state" = "Running" ] && podman_vm_running=true
      if ! $podman_vm_running; then
        echo "Starting the podman VM..."
        podman machine start
      fi
    fi
  '';
}
