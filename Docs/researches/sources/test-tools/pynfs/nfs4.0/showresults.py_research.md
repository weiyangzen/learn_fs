# sources/test-tools/pynfs/nfs4.0/showresults.py

Purpose: CLI utility to redisplay pickled pynfs server-test results with configurable pass/warn/fail/omit visibility.

Important APIs/types/functions: Imports `pickle`, `testmod`, and `OptionParser`. Functions are `show(filename, opt)`, `scan_options(p)`, and `main()`.

Control flow: When run directly, it adjusts `sys.path` for package-root execution, parses display options, requires one or more filenames, unpickles each file, and passes the loaded test list to `testmod.printresults`.

State and persistence behavior: Read-only against result pickle files; no output files are written.

Dependencies and integration points: Consumes pickle files written by `testserver.py --outfile`. Depends on `testmod.printresults` and compatible pickled test object classes.

Risks: Loading pickle files executes Python pickle deserialization and must not be used on untrusted files. The direct-run path check refers to `nfs4.1/testmod.py`, which looks suspicious for an NFSv4.0 script and may be stale.

Test signals: CLI errors if no filename is supplied. Successful operation is printed result summaries respecting `--show*`/`--hide*` flags.
