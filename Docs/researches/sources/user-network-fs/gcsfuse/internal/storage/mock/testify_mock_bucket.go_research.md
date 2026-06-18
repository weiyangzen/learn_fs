# sources/user-network-fs/gcsfuse/internal/storage/mock/testify_mock_bucket.go

## Purpose
This file defines the newer testify-based bucket mock for unit tests. It implements `gcs.Bucket` through `mock.Mock`.

## Important APIs and Control Flow
`TestifyMockBucket` implements all bucket methods by calling `m.Called(...)`, type-asserting return arguments, and returning either typed values or errors. Methods include name/type lookup, readers, object create/copy/compose/stat/list/update/delete/move, chunk and appendable writers, finalize/flush, folder operations, multi-range downloader creation, and `GCSName`.

## State, Dependencies, and Integration
State lives in the embedded testify mock. Dependencies are `context`, local `gcs`, and `testify/mock`. This mock integrates with unit tests that prefer testify expectations over deprecated oglemock code.

## Risks and Test Signals
Several methods use simplified call signatures compared with the real interface: for example `CreateObjectChunkWriter` calls `m.Called(ctx, req)` and ignores `chunkSize` and callback in expectation matching. Many return paths assume non-nil typed values when no error is configured and will panic if tests provide nil. This mock must be updated whenever `gcs.Bucket` changes.
