{ lib, buildGoModule, fetchFromGitHub }:

buildGoModule rec {
  pname = "talisman";
  version = "1.37.0";

  src = fetchFromGitHub {
    owner = "thoughtworks";
    repo = "talisman";
    rev = "v${version}";
    hash = "sha256-gdXyN+sFy60dAmkiUDLWllA8mnk3PnNMXT9xJ7/SUpg=";
  };

  vendorHash = "sha256-YxApJIF8ebzRBF5Fxh5/hQYHgKhC1/eQ4ra91+jdzPs=";

  subPackages = [ "." ];

  meta = with lib; {
    description = "Git hook that scans for potential secrets or sensitive information";
    homepage = "https://thoughtworks.github.io/talisman/";
    license = licenses.mit;
    maintainers = [ ];
    platforms = platforms.unix;
  };
}
