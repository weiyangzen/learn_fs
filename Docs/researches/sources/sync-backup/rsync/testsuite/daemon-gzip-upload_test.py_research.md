# sources/sync-backup/rsync/testsuite/daemon-gzip-upload_test.py

Purpose: verifies compressed daemon uploads with high verbosity/double `-z` style compression options.

Important APIs/types/functions: `build_rsyncd_conf`, `hands_setup`, `run_rsync`, `start_test_daemon`, and `checkit(['-avvvvzz', source, daemon-url])`.

Control flow: build hands tree and expected `CHKDIR` excluding daemon global `foobar.baz`, start daemon, then upload to `test-to` with `-avvvvzz` and compare daemon destination to expected tree.

State and persistence behavior: daemon writable destination must match filtered source tree after compressed upload.

Dependencies and integration points: daemon receiver compression path, test daemon config, and harness comparison.

Risks and test signals: allowed code 23 is tolerated. Failure indicates compressed daemon upload corruption or transfer failure.
