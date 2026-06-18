# Research: sources/sync-backup/syncthing/test/scan_test.go

## sources/sync-backup/syncthing/test/scan_test.go

Purpose: integration test for targeted subdirectory/file rescans.

Important APIs/functions: `TestScanSubdir`, `sender.RescanSub`, `sender.RescanDelay`, `rc.AwaitSync`, and directory comparison helpers.

Control flow: syncs initial h1/h2 data, delays full scans, then performs seven targeted scan scenarios: new file in known directory, new file in unknown directory, new deep file, new deep directory, deleted file in known directory, scan of missing deep path, and intentionally scanning only one of two new files to confirm unscanned changes do not sync.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes.

Dependencies and integration: scanner path targeting, database parent discovery, sync propagation. Risks include path normalization, delayed full scan masking targeted-scan behavior, and directory comparison expecting exact state. Test signal is equality after expected cases and deliberate inequality for the omitted file.
