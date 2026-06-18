# sources/test-tools/pynfs/nfs4.1/testserver.py

Purpose: command-line runner for pynfs NFSv4.1 server tests.

Important APIs/types/functions: `scan_options`, `Argtype`, `run_filter`, `printflags`, and `main`. Module-level defaults derive AUTH_SYS host/uid/gid values.

Control flow: `main` parses server URL and test selectors, creates test metadata from `server41tests`, handles display-only modes, validates `--use*` object paths, maps security names to RPC flavor/service pairs, checks supported security flavors, initializes `server41tests.environment.Environment`, runs tests, pickles optional result output, prints results, and optionally writes JSON or XML.

State and persistence behavior: writes optional pickle/JSON/XML result artifacts and triggers environment setup/cleanup that creates server-side test data. It also sets `environment.nfs4client.SHOW_TRAFFIC` and `environment.debug_fail` from options.

Dependencies/integration: uses `use_local`, `nfs4lib.parse_nfs_url`, `testmod`, `server41tests.environment`, `rpc.rpc` security constants/support table, `socket`, and `pickle`.

Risks and test signals: target path parsing expects byte strings for some path checks. The security mapping supports `krb5*` names only if `rpc.security.supported` includes `RPCSEC_GSS`. JSON and XML output are mutually exclusive due to `elif`.
