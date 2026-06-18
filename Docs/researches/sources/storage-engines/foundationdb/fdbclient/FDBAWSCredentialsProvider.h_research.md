# sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.h

## Purpose

`FDBAWSCredentialsProvider.h` declares the AWS credentials helper used by FoundationDB backup-related code when AWS backup support is enabled. The entire header content is guarded by `WITH_AWS_BACKUP`, so projects that do not build AWS backup support do not include AWS SDK declarations through this header.

## Important APIs, types, and functions

- Header guard: `FDB_AWS_CREDENTIALS_PROVIDER_H`, active only when `WITH_AWS_BACKUP` is defined.
- Includes:
  - `aws/core/Aws.h`
  - `aws/core/auth/AWSCredentialsProviderChain.h`
- Namespace: `FDBAWSCredentialsProvider`.
- Declaration: `Aws::Auth::AWSCredentials getAwsCredentials();`

## Control flow

The header has no runtime control flow. Preprocessor control flow is important: the outer guard is `#if (!defined FDB_AWS_CREDENTIALS_PROVIDER_H) && (defined WITH_AWS_BACKUP)`, followed by a redundant inner `#ifdef WITH_AWS_BACKUP`. If `WITH_AWS_BACKUP` is absent, the header expands to no declarations and no includes.

## State and persistence behavior

The header declares no state and performs no persistence. Runtime state lives in the `.cpp` implementation's one-time AWS SDK initialization flag and in AWS SDK internals.

## Dependencies and integration points

This header is a narrow boundary between fdbclient code and the AWS SDK. It allows AWS-dependent callers to request credentials without directly duplicating initialization logic. Because the declaration itself disappears when `WITH_AWS_BACKUP` is not defined, callers must also be conditionally compiled or otherwise avoid referencing `FDBAWSCredentialsProvider::getAwsCredentials()` in non-AWS builds.

## Risks and edge cases

- The conditional header guard means accidental inclusion in non-AWS builds silently provides no declaration. That is fine for guarded callers but can lead to confusing compile errors if a caller forgets its own `WITH_AWS_BACKUP` guard.
- The inner `#ifdef WITH_AWS_BACKUP` is redundant with the outer guard, but harmless.
- This header exposes AWS SDK types directly, so ABI and include-path compatibility are coupled to the configured AWS SDK.

## Test signals

There are no local tests. Build matrix coverage is important: one build with `WITH_AWS_BACKUP` should compile AWS SDK includes and the declaration, and one build without it should compile callers that correctly exclude AWS-specific use.
