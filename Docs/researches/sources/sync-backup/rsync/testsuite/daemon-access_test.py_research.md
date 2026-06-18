# sources/sync-backup/rsync/testsuite/daemon-access_test.py

Purpose: daemon module access-control coverage for read-only, read/write, write-only, hidden listing, and deep sub-path resolution.

Important APIs/types/functions: `write_daemon_conf`, `start_test_daemon`, `fails`, `run_rsync`, `verify_dirs`, `assert_same`, `walk_files`, and `rsync_argv`.

Control flow: build a depth-3 source and modules `ro`, `rw`, `wo`, and hidden `list=no`. Pull from read-only module and a deep sub-path, reject push to read-only, push to read/write, push to write-only and reject pull, inspect module listing for visible/hidden modules, then prove hidden module is still usable by explicit name.

State and persistence behavior: uses separate module backing directories for push/pull checks. Destination trees must match expected source paths.

Dependencies and integration points: daemon module permissions, module list generation, path resolution inside modules, and harness verify helpers.

Risks and test signals: allowed rsync code 23 is tolerated in some daemon transfers. Failures show access rule inversion, list leakage, or path resolution problems.
