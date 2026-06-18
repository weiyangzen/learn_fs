## sources/user-network-fs/gcsfuse/internal/storage/testify_mock_bucket.go

Purpose: Testify mock implementation of the internal `gcs.Bucket` interface for unit tests.

Important APIs/types/functions: `TestifyMockBucket` embeds `mock.Mock` and implements bucket operations: name/type, readers, object create/copy/compose/stat/list/update/delete/move, folder APIs, appendable/chunk writers, finalize/flush, multi-range downloader, and `GCSName`.

Control flow: each method calls `m.Called(...)`, type-asserts expected return values, and maps nil/error combinations to interface returns. Some methods pass simplified arguments, such as `FinalizeUpload` using `w.ObjectName()`.

State and persistence behavior: stores invocation expectations and call history in testify's mock state; no storage persistence.

Dependencies and integration points: supports tests across storage, file cache, writes, and folder logic that depend on `gcs.Bucket` without using the older Ogle mock.

Risks: several methods type-assert return values without nil guards, so tests must configure returns precisely. Argument lists differ from production signatures in a few methods, which can hide callback/chunk-size issues.

Test signals: no direct tests here; it is a test support adapter and failures surface in dependent suites.
