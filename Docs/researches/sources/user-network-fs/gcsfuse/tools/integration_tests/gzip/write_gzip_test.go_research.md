# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/write_gzip_test.go

Purpose: verifies overwriting gzip-related objects through the mounted filesystem writes the new raw content and updates GCS object size as expected.
Important APIs/functions: constant `overwrittenFileSize`; helper `verifyFullFileOverwrite`; five tests covering content-encoding/no-transform fixture variants.
Control flow: helper confirms the initial mounted file size matches the GCS object size, creates a 1000-byte temp file, copies it over the mounted object path with overwrite allowed, then re-queries GCS object size and expects exactly 1000 bytes.
State and persistence: mutates the overwrite-specific fixture objects under `gzip/`. Temp overwrite file is local and removed after use.
Dependencies and integration points: uses `client.GetGcsObjectSize`, `operations.StatFile`, `createContentOfSize`, `CreateLocalTempFile`, and `CopyFileAllowOverwrite`.
Risks and edge cases: validates size but not content or metadata after overwrite. Tests operate on separate `ToOverwrite` fixtures to avoid interfering with read tests.
Test signals: object size changes to `overwrittenFileSize` after mounted copy, confirming overwrite path is not preserving stale gzip metadata sizing.
