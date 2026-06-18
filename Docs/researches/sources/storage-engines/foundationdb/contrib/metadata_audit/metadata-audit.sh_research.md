# sources/storage-engines/foundationdb/contrib/metadata_audit/metadata-audit.sh

## Purpose
This shell wrapper provides a single entry point for metadata audit, backup, restore, and coalesce repair commands. It locates `libfdb_c`, finds an importable Python `fdb` package, ensures a cluster file is supplied or discoverable, then `exec`s the selected Python script.

## Important APIs, Types, And Functions
The command map supports `check`, `backup`, `restore`, and `repair-coalesce`, dispatching to `check_krm_corruption.py`, `backup_metadata.py`, `restore_metadata.py`, and `repair_coalesce.py`. Wrapper options are `--fdb-lib`, `--fdb-python`, and help. Environment inputs are `FDB_CLUSTER_FILE`, `FDB_LIB_PATH`, and `FDB_PYTHON_PATH`.

`find_fdb_lib` searches explicit flags, env vars, existing loader paths, build outputs, and standard library dirs for `libfdb_c.so` or `libfdb_c.dylib`. `find_fdb_python` searches explicit paths, env vars, current importability, build output bindings, lib-adjacent Python dirs, the script directory, and site-packages.

## Control Flow
The script uses `set -euo pipefail`, parses wrapper options before the command, maps command to script, locates and exports the dynamic library path, locates and prepends the Python binding path, prepends `SCRIPT_DIR` so shared utilities import, checks whether `-C/--cluster-file` appears in remaining args, and if not looks for `FDB_CLUSTER_FILE`, `/etc/foundationdb/fdb.cluster`, or `$HOME/.fdb/fdb.cluster`. It ends with `exec python3 "$SCRIPT" "$@"`.

## State And Persistence Behavior
The wrapper itself writes no persistent state. It changes process environment variables (`LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH`, `PYTHONPATH`) for the executed Python process. The selected Python command may read or mutate FDB metadata.

## Dependencies And Integration Points
It depends on Bash, `python3`, FoundationDB build/install layouts, and the sibling metadata audit Python scripts. It is the operational integration layer for users who may have built libraries rather than installed Python packages.

## Risks And Edge Cases
Wrapper options must precede the command; command-specific options after the command are not validated by the wrapper. The cluster-file check only detects presence of `-C` or `--cluster-file`, not whether the following value is valid. `DYLD_LIBRARY_PATH` can be restricted by macOS SIP for some child processes. The default search can accidentally pick a system `fdb` Python package incompatible with the selected `libfdb_c`.

## Test Signals
Shell tests should cover help, unknown wrapper option, unknown command, explicit and env library/Python paths, default cluster-file discovery, missing library/module/cluster diagnostics, and final `exec` argument preservation. Integration tests can run `check --dry`-style commands if available against a test cluster.
