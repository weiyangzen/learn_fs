# sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper_test.go

## Purpose
`control_client_wrapper_test.go` validates gcsfuse's Storage Control client wrappers. It verifies timeout-driven retry behavior, retryable versus non-retryable gRPC errors, storage-layout-only versus all-API retry modes, wrapper unnesting, and gax retry option installation.

## Important APIs, Types, and Functions
`stallingStorageControlClient` wraps a `StorageControlClient` and optionally delays `GetStorageLayout` and folder APIs until either a timer fires or the attempt context is cancelled. `ControlClientRetryWrapperTest`, `StorageLayoutRetryWrapperTest`, and `AllApiRetryWrapperTest` are testify suites around a `MockStorageControlClient`. `newHelperRetryWrapper` constructs a `newRetryWrapper` with small deadlines/backoffs to keep tests fast.

The gax-specific suite `ControlClientGaxRetryWrapperTest` checks `storageControlClientGaxRetryOptions` and `addGaxRetriesForFolderAPIs`.

## Control Flow
Storage-layout-only tests create a retry wrapper with folder retries disabled. They assert `GetStorageLayout` succeeds on first attempt, retries an `Unavailable` error then succeeds, wraps non-retryable `NotFound`, and times out without calling the raw client when the stalling layer exceeds per-attempt deadline. The same suite asserts folder APIs delegate directly and return a single retryable error without retry.

All-API tests repeat storage layout cases and then exercise `DeleteFolder`, `GetFolder`, `RenameFolder`, and `CreateFolder` for first-attempt success, retryable-error-then-success, non-retryable errors, and timeout. Wrapper factory tests assert `withRetryOnStorageLayout` and `withRetryOnAllAPIs` produce `*storageControlClientWithRetry`, set the right booleans, and unwrap an already wrapped client rather than nesting.

Gax tests resolve the returned `gax.CallOption`s to confirm retry settings exist and `codes.Unauthenticated` is currently treated as retryable. They also check nil input errors and that folder APIs receive two gax options while `GetStorageLayout` remains untouched by `addGaxRetriesForFolderAPIs`.

## State and Persistence Behavior
The test state is per-suite and in-memory: mock expectations, context, configured stall durations, and retry timing parameters. The tests depend on microsecond-scale timing, but there is no persistent state.

## Dependencies and Integration Points
The file depends on generated control protobufs, `control.RenameFolderOperation`, `gax`, `storageutil`, gRPC codes/status, testify assert/require/mock/suite, and the generated `MockStorageControlClient`. It directly validates the public helper behavior used during storage client setup.

## Risks and Edge Cases
Microsecond retry deadlines can be sensitive to scheduler delays; the tests avoid exact attempt counts in timeout cases and assert context deadline behavior. The helper method accepts a `controlClient` parameter but returns `newRetryWrapper(t.stallingClient, ...)`, so the suite is coupled to fixture state. The tests cover retry shape but not billing-project metadata wrapping.

## Test Signals
The file is the primary test signal for `control_client_wrapper.go`. It covers retry gating, retryable status handling, non-retryable error formatting, timeout cancellation before raw calls, all four folder APIs, unwrapping nested retry clients, gax option creation, unauthenticated retryability, and invalid gax-installation inputs.
