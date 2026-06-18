# sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.cpp

## Purpose

`FDBAWSCredentialsProvider.cpp` provides the FoundationDB client helper for retrieving AWS credentials when the build enables AWS backup support. The implementation is compiled only under `WITH_AWS_BACKUP`.

## Important APIs, types, and functions

- Namespace: `FDBAWSCredentialsProvider`.
- Function: `Aws::Auth::AWSCredentials getAwsCredentials()`.
- It uses `Aws::SDKOptions`, `Aws::InitAPI()`, `Aws::Auth::DefaultAWSCredentialsProviderChain`, and `TraceEvent`.

## Control flow

`getAwsCredentials()` uses a function-local static `bool doneInit` to initialize the AWS SDK once per process. On the first call it sets the flag, constructs default SDK options, calls `Aws::InitAPI(options)`, and emits `AWSSDKInitSuccessful`. Every call then constructs a default AWS credentials provider chain, asks it for credentials, and returns the resulting `Aws::Auth::AWSCredentials`.

The code intentionally does not call `Aws::ShutdownAPI()`. The comment explains that the AWS SDK is intended to live for the lifetime of the process.

## State and persistence behavior

The only local state is `doneInit`, which persists for the lifetime of the process. Credentials are not cached by this wrapper; it delegates caching/refresh behavior to the AWS SDK's default provider chain. No FoundationDB keys or files are written.

## Dependencies and integration points

The source includes `FDBAWSCredentialsProvider.h` and `fdbclient/Tracing.h`. Through the header it depends on AWS SDK core and auth provider-chain headers. Callers in backup/blob-store code can use this helper to obtain credentials without managing AWS SDK initialization themselves.

## Risks and edge cases

- `doneInit` is a plain function-local static boolean, not an atomic or `std::call_once`. In modern C++, initialization of the static variable itself is thread-safe, but writes to the bool are not protected if multiple threads enter the function concurrently after construction.
- If `Aws::InitAPI()` fails or has side effects that depend on options, this wrapper has no error path and no retry path.
- The process never shuts down the AWS SDK, by design. That avoids teardown ordering problems but can leak SDK-global resources until process exit.
- The default provider chain can read environment, profile, metadata, and other AWS-standard sources; behavior depends on deployment environment rather than FoundationDB configuration in this file.

## Test signals

There are no local tests. Coverage should come from AWS-backup builds and backup integration tests that verify credentials can be resolved from the expected default AWS provider sources. A targeted unit test would need to compile with `WITH_AWS_BACKUP` and control the AWS SDK credential environment.
