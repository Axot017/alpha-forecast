let pkgs = import <nixpkgs> { config = { allowUnfree = true; }; };
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.numpy
      python-pkgs.pandas
      python-pkgs.requests
      python-pkgs.selenium
      python-pkgs.beautifulsoup4
      python-pkgs.python-dotenv
    ]))
    pkgs.chromedriver
    pkgs.google-chrome
    (pkgs.writeShellScriptBin "chrome"
      "exec -a $0 ${pkgs.google-chrome}/bin/google-chrome-stable $@")

  ];
}
