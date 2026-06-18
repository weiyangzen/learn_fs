# Research: sources/sync-backup/syncthing/test/sync_test.go

## sources/sync-backup/syncthing/test/sync_test.go

Purpose: broad integration coverage for multi-device/multi-folder synchronization and sparse-file transfer efficiency.

Important APIs/functions: `TestSyncCluster`, `scSyncAndCompare`, and `TestSyncSparseFile`; constant `s12Folder` intentionally uses Unicode to verify arbitrary folder IDs.

Control flow: cluster test generates initial data on h1/h2/h3 and secondary folders, starts three instances, repeatedly forces delayed rescans, awaits sync across `default`, s12, and `s23`, compares actual directory contents to expected merged state, alters source folders, and appends to a file while preserving mtime to test content-change detection. Sparse test creates a mostly-zero large file, syncs two peers, compares directories, then asserts sender transferred less than 256 KiB.

State and persistence: mutates `s1`, `s2`, `s3`, `s12-*`, `s23-*`, and h1/h2/h3 indexes.

Dependencies and integration: `lib/rc`, connection/transfer layer, scanner hashing, folder ID handling, sparse block optimization. Risks include time limits, mtime granularity, fixed random seed expectations, and bandwidth byte threshold changes. Test signal is directory equality, remote in-sync checks, and connection byte totals.
