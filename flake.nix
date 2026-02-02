{
  description = "Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = { allowUnfree = true; };
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
            docker
            podman
            jq
          ];

          shellHook = ''
            has_pyproject=false

            [ -f "python/pyproject.toml" ] && has_pyproject=true

            if [ ! -d "python/.venv" ] && $has_pyproject; then
              cd python && uv sync && cd ..
            fi
          '';
        };
      }
    );
}
