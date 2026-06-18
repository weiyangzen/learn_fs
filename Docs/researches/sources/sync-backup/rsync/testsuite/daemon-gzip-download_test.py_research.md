# sources/sync-backup/rsync/testsuite/daemon-gzip-download_test.py

Purpose: verifies compressed daemon downloads with high verbosity/double `-z` style compression options, covering an old doubly-compressed transfer bug.

Important APIs/types/functions: `build_rsyncd_conf`, `hands_setup`, `run_rsync`, `start_test_daemon`, and `checkit(['-avvvvzz', daemon-url, dest])`.

Control flow: build hands tree and expected `CHKDIR` excluding daemon global `foobar.baz`, start daemon, then download `test-from` with `-avvvvzz` and compare to expected tree.

State and persistence behavior: destination must match the expected filtered source tree.

Dependencies and integration points: daemon sender compression path, optional TCP transport through harness, and directory comparison.

Risks and test signals: allowed code 23 is tolerated. Failure indicates compressed daemon download corruption or protocol failure.
