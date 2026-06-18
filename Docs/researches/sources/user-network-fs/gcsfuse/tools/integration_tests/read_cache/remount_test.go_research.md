# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/remount_test.go

Purpose: Verifies that file-cache state is not reused incorrectly across remounts, including dynamic mount path handling.

Important APIs/types/functions: `remountTest` follows the common suite lifecycle. `readFileAndValidateCacheWithGCSForDynamicMount` temporarily sets dynamic bucket state and adjusts `testEnv.testDirPath`. Tests use `remountGCSFuse`, `readFileAndValidateCacheWithGCS`, and structured read logs.

Control flow: normal remount test reads a file twice before remount and expects miss then hit, remounts, then reads twice again and expects miss then hit from the new mount/log. Dynamic remount test runs only for dynamic mounting, reads once, remounts, then expects the first read after remount to miss and the next to hit.

State/persistence: Remount clears in-memory cache/log context while the cache directory and GCS object may persist. Dynamic test manipulates package setup state to represent bucket-mounted path layout.

Dependencies/integration: Uses read-cache helpers, setup dynamic-bucket markers, storage client, and structured logs.

Risks/test signals: `readFileAndValidateCacheWithGCSForDynamicMount` mutates `testEnv.testDirPath`, so ordering and defer cleanup matter. Passing signals remount invalidates cache reuse boundaries while preserving later per-mount caching.
