{
    description = "todomd";
    
    inputs = {
	nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
	flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { self, nixpkgs, flake-utils, ...}: let
    	# This defines all packages that are shared across all builds of this project.
	# We defined it as a function because repo will change depending on the
	# architecture / os.
	# 
	# To add a new package, simply search for its name in https://search.nixos.org/packages
        commonPkgs = repo: with repo; [
	    python313
	    poetry
	];

	# eachDefaultSystem is a utility function that generates a configuration for
	# each available platform.
	in flake-utils.lib.eachDefaultSystem (system: let
	    sysNixpkgs = import nixpkgs { inherit system; };
	    in {

	        # This is the dev shell that can be invoked with "nix develop"
	        devShells.default = sysNixpkgs.mkShell {
		    packages = commonPkgs sysNixpkgs;
		    shellHook = with sysNixpkgs; ''
		        export ENV_NAME=todomd
			exec $SHELL
		    '';
		};

		# App that can be run with "nix run"
		apps.default = flake-utils.lib.mkApp {
		    drv = sysNixpkgs.writeShellScriptBin "todomd" ''
			cd ${self}
			${sysNixpkgs.poetry}/bin/poetry install
			${sysNixpkgs.poetry}/bin/poetry run python3 -m todomd.main "$@"
		    '';
		};
	    });
}
