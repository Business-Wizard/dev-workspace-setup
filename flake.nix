{
  description = "Development Environment";

  inputs = {
    # nixos-25.11 @ 2026-06-17
    nixpkgs.url = "github:NixOS/nixpkgs/d6df3513510aa548c83868fd22bfddd0a8c0a0d4";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            permittedInsecurePackages = [ "docker-28.5.2" ];
          };
          overlays = [ (import ./nix/overlays.nix) ];
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            git
            jujutsu
            prek
            uv
            cargo
            rustup
            vscode
            claude-code
            claude-monitor
            docker
            podman
            jq
            talisman
          ];

          shellHook = ''
            # Export UV_PYTHON to ensure uv uses Python 3.14
            export UV_PYTHON=python3.14

            # Auto-create and activate virtual environment (only if pyproject.toml exists)
            if [ -f pyproject.toml ] && [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              uv sync
            fi

            # Activate virtual environment
            if [ -f .venv/bin/activate ]; then
              source .venv/bin/activate
            fi

            # Install Talisman git hook if not already installed
            if [ -f .git/hooks ] && { [ ! -f .git/hooks/pre-commit ] || ! grep -q "talisman" .git/hooks/pre-commit 2>/dev/null; }; then
              echo "Installing Talisman pre-commit hook..."
              talisman --install-pre-commit-hook 2>/dev/null || echo "Note: Talisman will be available once nix build completes"
            fi
          '';
        };
      }
    );
}
