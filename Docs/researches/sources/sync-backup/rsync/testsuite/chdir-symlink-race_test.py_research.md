# sources/sync-backup/rsync/testsuite/chdir-symlink-race_test.py

Purpose: daemon receiver security regression for `chdir()` following an attacker-planted destination subdirectory symlink out of the module after earlier symlink-race hardening.

Important APIs/types/functions: `reset_outside`, `verify_unchanged`, `run_attack`, `positive_control`, `make_data_file`, daemon setup, and platform skip.

Control flow: create `module/subdir -> outside`, outside sentinel, and source files with matching size but different content/mode. Start writable daemon, prove ordinary writes to `realdir` work, then run four transfer shapes: single-file size-only into symlinked subdir, recursive size-only into subdir, recursive normal transfer into subdir, and recursive root upload regression check. Each must not signal-crash and must leave outside content/mode unchanged.

State and persistence behavior: outside sentinel is reset before every attack. Destination symlink state remains attacker-controlled.

Dependencies and integration points: daemon receiver chdir path, secure path traversal, size-only and delta/rename receiver flows, kernel support.

Risks and test signals: positive control guards against false passes caused by daemon refusal. Outside mode/content changes indicate chmod/write escape.
