# sources/user-network-fs/rclone/backend/filelu/filelu_helper.go

Purpose: This file provides FileLu backend utility methods for file-code lookup, feature/name/root/hash/precision methods, encoding conversion, retry classification, and root splitting.

Important APIs and types: `errFileNotFound`, `getFileCode`, `Features`, `fromStandardPath`, `toStandardPath`, `Hashes`, `Name`, `Root`, `Precision`, `String`, `isFileCode`, `shouldRetry`, `shouldRetryHTTP`, and `rootSplit`.

Control flow: `getFileCode` lists the parent directory and scans files for an exact server path match, returning the provider file code. `isFileCode` checks a strict 12-character lowercase alphanumeric shape. Retry helpers delegate to rclone retry rules and selected HTTP status codes. `rootSplit` separates the first path component from the rest.

State and persistence behavior: The helpers do not persist state. `getFileCode` performs a remote list and depends on current provider state.

Dependencies and integration points: `filelu_object.go` uses `getFileCode`, `isFileCode`, hash/metadata helpers, and retry helpers. `filelu_client.go` and upload code share the retry helpers.

Risks: `Hashes` advertises an empty set, while `Object.Hash` has an MD5 implementation for some file-code-derived cases, creating a capability mismatch. `getFileCode` relies on exact path construction after list normalization. `Precision` reports unsupported modtimes, while objects still cache `time.Now()` for listings and lookups.

Test signals: No direct helper tests exist; integration tests cover helper behavior only indirectly.
