# sources/test-tools/pynfs/nfs4.1/testclient.py

Purpose: command-line runner for pynfs NFSv4.1 client-side tests.

Important APIs/types/functions: `parse_useparams`, `scan_options`, `Argtype`, `run_filter`, `printflags`, and `main`.

Control flow: `main` parses options, builds tests from `client41tests` with `testmod.createtests`, handles `--showflags`/`--showcodes`, parses the server path, normalizes `--use*` paths, maps remaining arguments to flags or test codes, initializes `client41tests.environment.Environment`, runs tests via `testmod.runtests`, pickles results when requested, prints results, and calls environment cleanup.

State and persistence behavior: writes optional pickle output, mutates option fields for path/test selection, and creates/cleans server-side test state through the environment. It does not persist internal state beyond the output file.

Dependencies/integration: uses `use_local` path injection, `nfs4lib`, `testmod`, `client41tests.environment`, `socket`, `rpc.rpc`, and `pickle`. Security-option code is present but commented out.

Risks and test signals: `parse_useparams` assumes a non-`None` string, but the option default is `None`; the loop can call it if `attr == 'useparams'`. Result output file is opened in text mode while `pickle.dump` writes bytes in Python 3, which may be problematic if used.
