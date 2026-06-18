## sources/sync-backup/rsync/testsuite/rsyncfns.py

Purpose: shared Python helper module for the rsync testsuite, replacing the shell `rsync.fns` subset needed by rewritten tests.

Important APIs and state: validates required environment (`scratchdir`, `srcdir`, `TOOLDIR`, `RSYNC`), defines `SCRATCHDIR`, `SRCDIR`, `TOOLDIR`, `SUITEDIR`, `TMPDIR`, `FROMDIR`, `TODIR`, `CHKDIR`, `CHKFILE`, `OUTFILE`, `RSYNC_PEER`, `TLS_ARGS`, and `USE_TCP`, and normalizes umask/HOME. Result helpers are `test_fail`, `test_skipped`, and `test_xfail`.

Control flow and functions: rsync invocation helpers include `rsync_argv`, `forced_protocol`, and `run_rsync`. Daemon/port helpers include secure lock-file handling, `claim_ports`, `start_rsyncd`, `start_test_daemon`, and `require_tcp`. Filesystem/fixture helpers include `makepath`, `rmtree`, `cp_p`, `cp_touch`, `make_data_file`, `make_text_file`, `build_symlinks`, `hands_setup`, `make_tree`, `walk_files`, and `walk_dirs`. Verification helpers include `rsync_ls_lR`, `checkit`, `verify_dirs`, `v_filt`, `checkdiff`, `check_perms`, and path/property assertions. Ownership/xattr/daemon config helpers support privilege-sensitive and fake-super tests.

State and persistence: writes skip reasons, daemon config, lock files, output/listing diffs, temporary daemon processes, and may mutate global `TLS_ARGS`/`RSYNC`. It registers daemon cleanup with `atexit`.

Dependencies and integration: depends on POSIX tools (`find`, `sort`, `sed`, `xargs`, `diff`, `tls`), Python stdlib, and runner environment. It is the primary integration layer between executable tests and `runtests.py`.

Risks and test signals: helper bugs can cascade across the suite. Security-sensitive areas include `/tmp` lock-file validation, loopback daemon binding, and cleanup. Strong helper signals come from exact listing diffs, file diffs, itemize output diffs, and explicit skip/fail exit codes.
