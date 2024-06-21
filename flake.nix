# file: flake.nix
{
  description = "Python application packaged using poetry2nix and additional EDA tools";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
    nix-eda.url = "github:efabless/nix-eda";
    openlane2.url = "github:efabless/openlane2";
  };

  outputs = { self, nixpkgs, poetry2nix, nix-eda, openlane2 }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      edaPkgs = import nix-eda { inherit pkgs; };
      openlane = import openlane2 { inherit pkgs; };

      # Use the same Python version as OpenLane
      python = pkgs.python311Full;

      # create a custom "mkPoetryApplication" API function that under the hood uses
      # the packages and versions (python3, poetry etc.) from our pinned nixpkgs above:
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication defaultPoetryOverrides;

      pypkgs-build-requirements = {
        rectpack = [ "setuptools" ];
        vlsir = [ "setuptools" ];
        vlsirtools = [ "setuptools" ];
        hdl21 = [ "flit-core" ];
        sky130-hdl21 = [ "flit-core" ];
        gdsfactory = [ "flit-core" ];
        sky130 = [ "flit-core" ];
        thewalrus = [ "setuptools" ];
      };
      custom_overrides = defaultPoetryOverrides.extend (final: prev:
        builtins.mapAttrs (package: build-requirements:
          (builtins.getAttr package prev).overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg prev else pkg) build-requirements);
          })
        ) pypkgs-build-requirements
      );

      app = mkPoetryApplication {
        projectDir = ./.;
        preferWheels = true;
        extras = [] ;
        overrides = custom_overrides;
        python=python;
      };

      # Test support for overriding the app passed to the environment
      # Override app to depend on hatchling and scikit-build-core
      overridden = app.overrideAttrs (old: {
        name = "${old.pname}-overridden-${old.version}";
        nativeBuildInputs = old.nativeBuildInputs or [] ++ [
          pkgs.python3Packages.hatchling
          pkgs.python3Packages.scikit-build-core
          pkgs.python3Packages.scikit-learn
        ];
        # Include scikit-build-core in propagatedBuildInputs to ensure it's available to dependencies
        propagatedBuildInputs = old.propagatedBuildInputs or [] ++ [
          pkgs.python3Packages.hatchling
          pkgs.python3Packages.scikit-build-core
          pkgs.python3Packages.scikit-learn
        ];
      });

      depEnv = app.dependencyEnv.override {
        app = overridden;
      };
      packages.x86_64-linux.piel = nixpkgs.legacyPackages.x86_64-linux.piel;

    in
    {
        packages.${system} = {
            default = app;
            python = python;
        };

        apps.${system}.default = {
            type = "app";
            # replace <script> with the name in the [tool.poetry.scripts] section of your pyproject.toml
            program = "${app}/bin/piel";
        };

        shell.${system}.default = pkgs.mkShell {
        buildInputs = [
          app
          edaPkgs.ngspice
          edaPkgs.xschem
          edaPkgs.verilator
          edaPkgs.yosys
          openlane.openlane2
          pkgs.verilog
          pkgs.gtkwave
        ];
        # Optionally, set PYTHONPATH to include the app's path in other shells if needed
        shellHook = ''
            echo "Setting Piel-Nix Environment Up"
            export PATH=${app}/bin:$PATH
            export PATH=${app}/lib/python${python.version}/site-packages:$PATH
        '';
        };

        devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          app
          edaPkgs.ngspice
          edaPkgs.xschem
          edaPkgs.verilator
          edaPkgs.yosys
          openlane.openlane2
          pkgs.verilog
          pkgs.gtkwave
        ];
        # Optionally, set PYTHONPATH to include the app's path in other shells if needed
        shellHook = ''
            echo "Setting Piel-Nix Environment Up"
            export PATH=${app}/bin:$PATH
            export PATH=${app}/lib/python${python.version}/site-packages:$PATH
        '';
        };

    };
}