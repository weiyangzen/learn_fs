<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/suite_test.go -->
# sources/object-store/minio-mc/cmd/suite_test.go

Purpose: this file is a gated full integration test suite for `mc`, enabled only when `MC_TEST_RUN_FULL_SUITE=true`. It builds or locates the `mc` binary, configures an alias against a MinIO endpoint, creates temporary local files and buckets, then exercises a broad set of end-user commands: alias, admin user, share upload/download, cp/cat/pipe/mirror/rm/stat/ls/du/find, bucket error cases, and server-side encryption modes.

Important APIs/types/functions: `Test_FullSuite` is the orchestrator; `initializeTestSuite`, `preflightCheck`, `preRunCleanup`, and `postRunCleanup` own environment setup and teardown. `newTestFile` and `testFile` model generated local files plus observed MinIO object metadata. Helpers such as `RunMC`, `RunCommand`, JSON parsers, `CreateBucket`, `createFile`, `openFileAndGetMd5Sum`, and fatal wrappers provide the test harness. Encryption coverage is split across SSE-C, SSE-KMS, and SSE-S3 helpers.

Control flow: setup reads many `MC_TEST_*` variables, optionally builds `../mc`, fills deterministic/random file fixtures, configures global CLI flags, registers users, and creates two buckets. The dependent lane uploads fixtures, captures `ls`/`stat` outputs into `fileMap`, validates metadata, then tests pipe, mirror, tag preservation, find filters, and downloads. Optional branches run HTTPS-only SSE-C tests, KMS-only tests, SSE-S3 tests, and KMS-to-SSE-C copy tests.

State and persistence: the suite mutates real MinIO state by creating buckets, users, policies, objects, tags, metadata, and encryption-protected objects. It writes temporary local files under `tempDir`, may build `../mc`, stores bucket/user names in package-level maps/slices, and deletes buckets/users/temp files at cleanup.

Dependencies and integration points: it shells out to `go build`, `curl`, and the generated `mc` binary, and depends on a reachable MinIO server, configured credentials, optional HTTPS/KMS/SSE-S3 support, and JSON output schemas from many command implementations in the same package.

Risks and test signals: because tests share global mutable state and depend on external services, order matters and failures can cascade. The suite is valuable as an end-to-end regression signal for CLI compatibility, JSON contracts, object metadata, encryption flags, and cleanup behavior, but it is unsuitable for normal fast unit-test lanes without the environment gate.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/suite_test.go -->
