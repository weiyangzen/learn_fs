# sources/sync-backup/rsync/testsuite/daemon-path-root-read_test.py

Purpose: functional regression for daemon modules with `path = /` and `use chroot = no`, where secure sender open could reject absolute module-root paths with EINVAL.

Important APIs/types/functions: `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-a', url-root-subpath, dest)`, `test_xfail`, and content checks.

Control flow: create a served subtree under scratch, configure a read-only daemon module rooted at `/`, request the served subtree by stripping the leading slash in the daemon URL, and inspect output. If the known `Invalid argument (22)` symptom appears, mark xfail. Otherwise require successful transfer and exact content for root and nested files.

State and persistence behavior: destination should receive `README` and `sub/deep.txt` from the absolute path served through root module.

Dependencies and integration points: daemon sender file open hardening, module-root path handling, and test xfail mechanism.

Risks and test signals: currently may xfail on affected versions. Unexpected nonzero exit or content mismatch after the known symptom is absent is a failure.
