<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light_test.go

This file tests the lightweight Kopia metadata persister. The tests create temp repositories, store/load/delete metadata keys, verify missing keys produce expected errors, and exercise repeated updates through Kopia snapshots.

The control-flow signal validates that the in-process Kopia client can initialize/connect, snapshot virtual files, restore latest values, and delete manifests for a key. It also indirectly validates per-key locking by using the public store/load/delete API, though not as a stress test.

Risks not fully covered include heavy concurrent same-key access, S3 storage, cache limit behavior, and process crash between metadata operations. Dependencies are `require`, temp filesystem storage, and robustness sentinel errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light_test.go -->
