# sources/sync-backup/rsync/testsuite/sender-flist-symlink-leak_test.py

Purpose: Python regression test for a daemon sender file-list leak where `change_pathname()` and `change_dir()` could follow an attacker-controlled directory symlink outside a no-chroot daemon module during listing. It verifies that a pull of `rsync://daemon/module/cd/`, where `cd` points outside the module, does not enumerate outside names.

Important APIs and flow: imports `SCRATCHDIR`, `rsync_argv`, `start_test_daemon`, identity helpers, and failure/skip helpers from `rsyncfns`. It skips platforms lacking the secure resolver primitive, creates `module/`, `outside/`, a marker file, and `module/cd -> outside`, then writes a temporary `rsyncd.conf`. A positive-control dry-run recursive daemon pull of `realdir/` must list `in_module.txt`; only then does the leak probe dry-run-pull `cd/` and scan stdout/stderr for `leak_marker.txt`.

State and persistence: all state lives in scratch directories and a generated daemon config/log. The daemon port is fixed at `12881`, so concurrent runs need the harness to isolate workers or serialize daemon tests.

Dependencies and integration: exercises daemon-mode path resolution, sender flist generation, `start_test_daemon()`, and the secure `change_dir()` behavior in the C code. Risks are platform-specific skip accuracy, fixed port collision, and false confidence if the positive control is weakened. Test signal is binary: any marker listing is a metadata leak; daemon crash by signal is also failure.
