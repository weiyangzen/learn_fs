# sources/test-tools/pynfs/nfs4.0/testserver.py

Purpose: Main NFSv4.0 pynfs server test runner. It parses server URL/options, builds the test database, selects tests by flags/codes, initializes the test environment, runs tests, prints and optionally serializes results.

Important APIs/types/functions: Imports `nfs4lib`, `testmod`, `servertests.environment`, `rpc.rpc`, `pickle`, `socket`, and `optparse`. Key functions/classes are `unixpath2comps`, `scan_options`, `Argtype`, `run_filter`, `printflags`, and `main`. Constants include `VERSION`, `HOST`, `UID`, and `GID`.

Control flow: `main` parses options, creates tests via `testmod.createtests('servertests')`, handles informational listing modes, parses `SERVER:/PATH`, normalizes `--use*` paths, maps security flavor to RPC auth classes, converts remaining args to include/exclude flag/code selectors, initializes `environment.Environment`, runs `testmod.runtests`, pickles output if requested, finalizes environment, prints results, and writes JSON/XML if requested.

State and persistence behavior: Mutates `nfs4lib.SHOW_TRAFFIC`, environment debug flags, option fields, and test result objects. Can create cleanup/output files through environment and result serialization.

Dependencies and integration points: The central integration point for all `servertests/st_*.py` modules. It depends on test docstring metadata parsed by `testmod`, RPC security support registry, NFS URL parsing, and environment setup/cleanup.

Risks: Test selection defaults to no tests unless flags/codes are supplied. Pickle output is binary and version-coupled to test classes. Initialization failures raise after printing hints, so automation must capture stack traces. `printflags` contains bare `print` statements without parentheses that are no-ops under Python 3 when intended as blank lines.

Test signals: Exit behavior follows result count: initialization errors exit/raise, `nfail < 0` exits `3`, and normal output comes from `testmod.printresults`; optional JSON/XML outputs are written by `testmod`.
