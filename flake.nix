{
  description = "Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/0182a361324364ae3f436a63005877674cf45efb";
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
            claude-monitor
            docker
            podman
            jq
          ];
        };
      }
    );
}
