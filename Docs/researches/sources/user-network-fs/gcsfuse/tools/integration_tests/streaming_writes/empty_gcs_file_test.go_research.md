# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/empty_gcs_file_test.go

## Purpose

Defines the streaming-writes suite variant where the file already exists as an empty GCS object before it is opened through the mount. This exercises takeover and write buffering for synced-but-empty objects.

## Important APIs, control flow, and dependencies

`streamingWritesEmptyGCSFileTestSuite` embeds `StreamingWritesSuite` and `suite.Suite`. `SetupTest` and `SetupSubTest` both call `createEmptyGCSFile`, which generates a unique name, creates an empty object with `CreateObjectInGCSTestDir`, validates it with `ValidateObjectContentsFromGCS`, records `filePath`, and opens with `operations.OpenFileWithODirect`. `TestEmptyGCSFileTestSuiteTest` wires the embedded testify suite and runs all inherited test methods.

## State, persistence, dependencies, and integration points

The suite starts every test from a durable empty GCS object, not just a local inode. This matters for read-after-write, rename, truncate, symlink, and out-of-order write methods inherited from `StreamingWritesSuite`, because gcsfuse must preserve object-generation correctness while streaming data into an existing object.

## Risks and test signals

Risks include setup reuse across subtests, precondition failures when the object already exists, and O_DIRECT alignment assumptions in the operation helper. Signals come from the inherited tests: exact readback, GCS content validation after close, rename/delete semantics, and no unexpected object-not-found errors for the initial empty object.
