## sources/sync-backup/rsync/testsuite/reverse-daemon-delta_test.py

Purpose: version-mixing smoke test for old client to current daemon and current daemon to old client, ensuring delta transfer still engages in both directions with and without compression.

Important APIs and control flow: starts a daemon using current `RSYNC`, drives the client with `RSYNC_PEER`, and parses old/new rsync summary formats via regex. `make_versions()` creates related old/new files with shared blocks and changed tail. `peer_client()` runs the peer binary and returns sent/received bytes. `assert_delta()` requires moved bytes less than half the file size. `run_push()` and `run_pull()` cover sender/receiver roles, each with optional `-z`.

State and dependencies: daemon config, fixed port 12894, `FROMDIR`, `TODIR`, `TMPDIR/client-src`, `TMPDIR/client-dst`, locale forced to C.

Integration points: daemon protocol compatibility, delta algorithm, compression, and alternate client/server binaries.

Risks and test signals: summary parsing must handle old wording. File content equality plus low wire bytes prove delta behavior rather than whole-file copying.
