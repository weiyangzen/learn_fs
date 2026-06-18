# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/write_large_files_test.go

Purpose: package-level `TestMain` and shared constants/state for large-file write integration tests.

Important APIs/types/functions: constants `TmpDir`, `OneMiB`, `WritePermission_0200`, package globals `storageClient` and `ctx`, and `TestMain`.

Control flow: parses setup flags, loads common YAML config or synthesizes default write-large-files configs, creates a storage client, determines bucket type, supports mounted-directory mode, builds compatible flag sets, sets up test dirs, mounts statically, and exits with the test result.

State/persistence behavior: initializes package storage client and setup globals, creates build/mount temp directories, and mounts/unmounts through static mounting.

Dependencies/integration: ties together `client`, `setup`, `test_suite`, and `static_mounting`.

Risks/test signals: falls back to hard-coded flags when config is absent, including streaming-writes disabled and write block limits. Mounted-directory mode requires both bucket and mount path because tests compare mounted data with bucket-visible content.
