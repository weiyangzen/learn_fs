# sources/user-network-fs/rclone/backend/onedrive/onedrive_test.go

Purpose: supplies the generic rclone integration test entry points for the OneDrive backend and exposes test-only upload chunk size control.

Important APIs: `TestIntegration` runs `fstests.Run` against `TestOneDrive:` with `NilObject: (*Object)(nil)`. `TestIntegrationCn` runs the same suite against `TestOneDriveCn:` unless a `-remote` flag is supplied. `(*Fs).SetUploadChunkSize` delegates to the production `setUploadChunkSize`, and the compile-time assertion registers `Fs` as `fstests.SetUploadChunkSizer`.

Control flow: the integration suite exercises rclone's generic filesystem contract. The `ChunkedUpload` config uses `fstests.NextMultipleOf(chunkSizeMultiple)`, ensuring test-selected chunk sizes respect OneDrive's required 320 KiB multiple. The China test has a guard to avoid conflicting with an explicitly requested remote.

State and persistence behavior: these tests operate on configured live remotes and rely on fstests to create, mutate, and clean remote objects. The file itself holds no persistent state.

Dependencies and integration points: depends on `fs`, `fstest`, and `fstests`. It is coupled to the production `chunkSizeMultiple` constant and `setUploadChunkSize` validation path.

Risks: coverage depends on externally configured `TestOneDrive:` and `TestOneDriveCn:` remotes. The China test is easy to skip unintentionally when `-remote` is set. Generic fstests cover core behavior but not all metadata and permission nuances; those are in `onedrive_internal_test.go`.

Test signals: confirms the backend participates in the standard rclone contract and that chunk-size mutation works under the generic chunked upload test harness.
