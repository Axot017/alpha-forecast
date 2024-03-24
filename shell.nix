with import <nixpkgs> { config = { allowUnfree = true; }; };
with pkgs.python3Packages;
let
  keras = buildPythonPackage rec {
    pname = "keras";
    version = "2.13.1";
    src = fetchPypi {
      inherit pname version;
      sha256 = "sha256-XfEswkGgFaEbZd20UsDusnRPziHZtUukjbh0klaMzGg=";
    };
    doCheck = false;
    propagatedBuildInputs = [ setuptools ];
    buildInputs = [ python3 ];
  };
in mkShell {
  packages = [
    (python3.withPackages (python-pkgs:
      with python-pkgs; [
        pip
        numpy
        pandas
        requests
        selenium
        beautifulsoup4
        python-dotenv
        keras
        tensorflow
        scikit-learn
      ]))
    chromedriver
    google-chrome
    (writeShellScriptBin "chrome"
      "exec -a $0 ${pkgs.google-chrome}/bin/google-chrome-stable $@")

  ];
}
