<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiaclient/kopiaclient.go -->
# sources/sync-backup/kopia/tests/tools/kopiaclient/kopiaclient.go

This file provides an in-process Kopia repository client used by the lightweight metadata persister. `KopiaClient` stores config path and password, and can create/connect, set cache limits, create snapshots from virtual key/value files, restore latest values, and delete all snapshots for a key.

`CreateOrConnectRepo` chooses S3 or filesystem storage, initializes if needed, then connects. `SnapshotCreate` opens the repo, creates a write session, builds source info and policy, uploads a virtual directory containing `data`, saves the snapshot manifest, flushes, and closes. `SnapshotRestore` lists snapshots for a key, picks the latest by start time, opens `root/data`, and reads bytes. `SnapshotDelete` deletes all manifests for the key. Helpers select storage, build virtual sources, source info, and latest manifest.

State persists in Kopia repository manifests/contents. Dependencies are repo/blob/snapshot internals, S3 env credentials, virtualfs, and robustness `ErrKeyNotFound`. Risks include repository handles not closed on early errors, latest selection by timestamp, hardcoded password/endpoint for tests, and deleting all key manifests. Persister-light tests validate integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiaclient/kopiaclient.go -->
