# sources/sync-backup/restic/cmd/restic/integration_helpers_test.go

Purpose: shared integration-test support for command tests in this package.

Important APIs/types/functions: `dirEntry`; `walkDir`; `directoriesContentsDiff`; `dirStats`; `testEnvironment`; `withTestEnvironment`; `testSetupBackupData`; `listPacks`; `listTreePacks`; `captureBackend`; `removePacks`; `removePacksExcept`; `loadSnapshotMap`; `lastSnapshot`; `testLoadSnapshot`; `appendRandomData`; `testFileSize`; `withCaptureStdout`; `withTermStatus`; `withTermStatusRaw`.

Control flow and state: creates temp local repos/caches/mountpoints/testdata with low-security test KDF and fast retries, installs a default backend hook that detects multiple listings, and returns cleanup. Helpers compare restored directory trees, directly remove packs through captured backend, load snapshots, generate random files, capture stdout, and install terminal status wrappers.

Dependencies and integration points: central dependency for most integration tests; uses backend/all, retry, repository test knobs, restic fixtures, termstatus, progress printers, and OS filesystem APIs.

Risks: direct backend and filesystem manipulation is powerful and local-backend-oriented. Default list-once hook requires tests to disable it when repeated listings are expected. Directory comparison depends on OS-specific `dirEntry.equals`.

Test signals: not a test itself but enables broad command integration coverage and fault injection.
