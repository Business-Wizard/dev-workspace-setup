{ lib, buildGoModule, fetchFromGitHub }:

buildGoModule rec {
  pname = "talisman";
  version = "1.37.0";

  src = fetchFromGitHub {
    owner = "thoughtworks";
    repo = "talisman";
    rev = "v${version}";
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  vendorHash = "sha256-BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=";

  subPackages = [ "." ];

  meta = with lib; {
    description = "Git hook that scans for potential secrets or sensitive information";
    homepage = "https://thoughtworks.github.io/talisman/";
    license = licenses.mit;
    maintainers = [ ];
    platforms = platforms.unix;
  };
}
