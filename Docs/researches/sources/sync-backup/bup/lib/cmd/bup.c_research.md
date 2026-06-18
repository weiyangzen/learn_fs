## sources/sync-backup/bup/lib/cmd/bup.c

Purpose: native launcher for the `bup` command. It locates the installed library directory, prepends it to `PYTHONPATH`, exposes original argv through an embedded `bup_main` Python module, and starts Python with `-m bup.main` or development entry modes.

Important APIs and control flow: `get_argv()` returns C argv as Python bytes. `setup_bup_main_module()` records original `PYTHONPATH` and registers the module. Platform-specific `exe_parent_dir()` resolves the executable using macOS `_NSGetExecutablePath`, FreeBSD `sysctl`, Linux/Sun `/proc`, or PATH search plus `realpath`. `prepend_lib_to_pythonpath()` validates the lib dir and updates the environment. Three `main()` variants handle normal, `BUP_DEV_BUP_PYTHON`, and `BUP_DEV_BUP_EXEC` builds.

State and dependencies: process-global state stores argv and original Python path. It depends on Python C API, `bup/intprops.h` for overflow-safe buffer doubling, and `bup/io.h` for fatal diagnostics.

Risks and tests: path discovery is platform-sensitive; failures abort with Bup exit status 2. Python <3.7 is rejected at compile time, and Python <3.8 uses `bup_py_bytes_main()`. Test signals include `test-install` for installed launcher behavior, `test-help` for main command dispatch, and `test_argv.py` outside this subset for argv semantics.
