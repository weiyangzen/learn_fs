# sources/test-tools/pynfs/nfs4.0/setup.py

Purpose: setuptools packaging script for the NFSv4.0 pynfs package, with eager generation of Python XDR support files from `.x` definitions before packaging/install.

Important APIs/types/functions: Imports `setuptools.setup`, `setuptools.modified.newer_group` or legacy `setuptools.dep_util.newer_group`, `glob`, `xdrgen`, `use_local`, and `VERSION` from `testserver`. Functions are `needs_updating(xdrfile)`, `use_xdr(dir, xdrfile)`, and `generate_files()`.

Control flow: On import/execution it adjusts `sys.path` when run from the package root, falls back to `use_local` if `xdrgen` is not importable, calls `generate_files()` unconditionally, then invokes `setup()`. `generate_files` regenerates NFSv4, NFSv3, RPC, and GSS XDR modules if source `.x` files are newer than generated `_const.py`, `_type.py`, and `_pack.py` targets.

State and persistence behavior: Changes process working directory while generating files, writes generated Python modules via `xdrgen.run`, and deletes parser artifacts matching `parse*` in each XDR directory. Packaging metadata installs packages from `lib`.

Dependencies and integration points: Integrates with local `xdrgen`, `testserver.VERSION`, `lib/testmod.py`, `xdrdef`, `lib/rpc`, and setuptools. Scripts installed are `testserver.py` and `showresults.py`.

Risks: Unconditional generation during setup import can mutate the source tree unexpectedly. Working-directory changes require the final `os.chdir(home)` path to run. Deleting `parse*` is broad within target directories.

Test signals: No direct tests; success is observable through generated XDR modules being current and `setup()` completing. Install mode prints `PYTHONPATH` guidance.
