# sources/user-network-fs/gcsfuse/internal/storage/mock/mock_writer.go

## Purpose
This file defines a testify-based mock writer implementing the `gcs.Writer` surface for unit tests.

## Important APIs and Control Flow
`Writer` embeds `io.WriteCloser`, `storage.ObjectAttrs`, and `mock.Mock`. `Write`, `Attrs`, `Close`, `Flush`, and `ObjectName` delegate to `mw.Called(...)` and cast returned arguments into the expected types. This lets tests set expectations on upload writes, flushes, close/finalize behavior, object attributes, and object name.

## State, Dependencies, and Integration
State is held by `testify/mock.Mock`, which records calls and configured returns. Dependencies include `io`, `cloud.google.com/go/storage`, and `testify/mock`. It is used with `mock.TestifyMockBucket` and write-path tests that need controlled writer behavior without real GCS.

## Risks and Test Signals
The methods assume the test configured return values with exact types; missing or nil `Attrs`/`Flush` return values will panic during type assertions. This is normal for strict mocks but makes test failures abrupt.
