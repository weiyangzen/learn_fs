# sources/sync-backup/rsync/testsuite/daemon-refuse-compress_test.py

Purpose: verifies a daemon module configured with `refuse options = compress` rejects compressed clients but still serves uncompressed clients.

Important APIs/types/functions: `build_rsyncd_conf`, appended module config, `start_test_daemon`, `rsync_argv('-avz')`, `checkit`, and stderr check for `--compress`.

Control flow: append `no-compress` module to base config, build hands tree and expected `CHKDIR`, start daemon, run a compressed download and require nonzero exit plus refusal text mentioning `--compress`, then run the same download without `-z` and compare to expected data.

State and persistence behavior: destination is reset between refused and allowed runs. Error output is persisted to `SCRATCHDIR/refuse.err`.

Dependencies and integration points: daemon refuse-options matching for aliases (`-z`/compress), module config, and harness comparison.

Risks and test signals: failure means compression was not refused or refusal blocked allowed transfers.
