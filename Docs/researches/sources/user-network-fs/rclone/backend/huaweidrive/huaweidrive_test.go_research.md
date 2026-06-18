<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive_test.go -->
## Research: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive_test.go

### Purpose
This file is a broad test suite for the Huawei Drive rclone backend. It combines a real integration test entry point, constructor and interface checks, encoding and query-filter unit tests, API type and response-shape validation, retry/error classification tests, and behavioral assertions for metadata, modtime, MIME type, upload mode selection, domain mapping, and root-folder detection logic. It is not production code, but it documents many backend contracts that the implementation is expected to preserve.

### Important APIs, Types, and Functions
Key test targets include `NewFs`, `Fs.Name`, `Fs.Root`, `Fs.String`, `Fs.Precision`, `Fs.Hashes`, `Object.Hash`, `Object.Storable`, `Object.String`, `Object.SetModTime`, `Object.MimeType`, `parsePath`, `NewQueryFilter`, and the `QueryFilter` builder methods. It also validates package constants such as `rcloneClientID`, `rootURL`, `uploadURL`, `defaultChunkSize`, `retryErrorCodes`, OAuth scopes and auth/token URLs, and API constants from `backend/huaweidrive/api`.

`TestIntegration` delegates to `fstests.Run` against `TestHuaweiDrive:` and declares the backend's NilObject and Windows-character skip behavior. Compile-time interface tests assert that `Fs` implements `fs.Fs`, `fs.Copier`, `fs.Mover`, `fs.DirMover`, `fs.ListRer`, `fs.Abouter`, `fs.Purger`, `fs.CleanUpper`, `fs.UserInfoer`, `fs.Disconnecter`, and `fs.DirCacheFlusher`, while `Object` implements `fs.MimeTyper`.

### Control Flow and Behavior
The tests cover construction failure for empty config, simple accessors, and Huawei's no-modtime-preservation behavior. Encoding tests build the expected `encoder.MultiEncoder` flags and verify full-width or visible replacement of reserved characters, leading/trailing spaces, leading dots/tildes, right periods, path separators, invalid UTF-8/control characters, and round-tripping where possible.

`TestQueryFilter` exercises composable filtering by parent folder, MIME type equality/inequality, filename equality and containment, recycled/directly-recycled flags, favorites, and edited-time ranges. It also verifies quote escaping in filenames. Later tests use small in-memory examples to model root-folder detection: prefer parent IDs that are not themselves file IDs, then fall back to the most common parent when all parents are known file IDs.

### State and Persistence
The file directly inspects lightweight state such as `Fs.rootFolderID`, `Options.RootFolderID`, `Options.ChunkSize`, `Options.ListChunk`, `Options.UploadCutoff`, and object metadata fields (`remote`, `size`, `modTime`, `id`, `sha256`, `mimeType`, `hasMetaData`). It does not persist state itself, but its assertions pin config defaults, cached root-folder behavior, and auth/domain configuration that production code depends on.

### Dependencies and Integration Points
The tests depend on rclone core packages (`fs`, `fstest/fstests`, `configmap`, `hash`, `encoder`), the Huawei API type package, standard `mime`, `path`, `time`, and HTTP primitives. `TestIntegration` is the only test that expects a configured live remote; the rest are unit-level checks over local structs and pure helpers.

### Risks and Edge Cases
The suite highlights risk areas: Huawei rejects many filename characters; modtimes are not preserved even if API parameters exist; only SHA256 is expected; temporary Huawei error codes must remain retryable; some MIME detections vary by host OS; root-folder auto-detection can be heuristic; and changing OAuth scopes, URLs, or domain maps can break authentication or regional routing. Several tests model behavior rather than calling the exact production function, so they can drift if the implementation changes without the test being updated to exercise the real path.

### Test Signals
The test file itself is the signal. It provides regression coverage for encoding policy, query generation strings, API JSON model fields, retry/non-retry classification, upload type thresholds, interface conformance, and object metadata methods. The integration test is gated by availability of `TestHuaweiDrive:` and is likely skipped or externally configured in normal CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive_test.go -->
