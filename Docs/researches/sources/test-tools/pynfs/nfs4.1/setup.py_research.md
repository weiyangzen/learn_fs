# sources/test-tools/pynfs/nfs4.1/setup.py

Purpose: setuptools packaging script for the `nfs4` Python package, with a custom build step to generate Python modules from XDR definition files.

Important APIs/types/functions: custom `build_py` subclass, `build_packages`, `expand_xdr`, and the final `setup(...)` call.

Control flow: import `xdrgen`, falling back through `use_local` if needed. During build, `build_packages` calls `expand_xdr` for each package directory before finding/building modules. `expand_xdr` changes into `<package_dir>/xdrdef`, runs `xdrgen.run` on each `*.x` file, attempts to remove parser artifacts, and returns to the original cwd in a `finally`.

State and persistence behavior: generates or overwrites `_const.py`, `_pack.py`, and `_type.py` style generated modules under `xdrdef`; removes `parser.out` and `parsetab.py` when present. Package metadata itself is static.

Dependencies/integration: integrates setuptools, local `xdrgen`, globbing, and package layout `{"nfs4": ""}` with package names `nfs4` and `nfs4.server41tests`.

Risks and test signals: build behavior depends on current working directory and local `use_local` path injection. Broad `except` during parser artifact cleanup can hide cleanup errors, though it prints a message.
