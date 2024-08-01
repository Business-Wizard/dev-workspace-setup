let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in

let
  shell_packages = with pkgs; [
    pre-commit
    rye
  ];
in

pkgs.mkShell {
  buildInputs = shell_packages;

  shellHook = ''
    if [ ! -d ".venv" ]; then
      echo "Creating a virtual environment..."
      rye sync
    fi

    echo "Activating the virtual environment..."
    source .venv/bin/activate
  '';
}
