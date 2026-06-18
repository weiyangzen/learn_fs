# sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.cc

## Purpose

This file implements `TPFallBackCopyJob`, a copy job wrapper that prefers third-party copy and falls back to classic streaming copy only for configured, retryable TPC support failures.

## Important APIs, Types, and Functions

The constructor logs source and target. The destructor deletes the currently allocated delegate job. `Run` reads the `thirdParty` property, creates a `ThirdPartyCopyJob`, runs it, and conditionally replaces it with `ClassicCopyJob`.

## Control Flow

If `thirdParty` is `"first"`, fallback is enabled. `Run` executes TPC first. Success returns immediately. If fallback is enabled and TPC returns `errNotSupported` or `errOperationExpired`, the wrapper logs the downgrade, deletes the TPC job, creates a classic streaming job, and runs it with the same progress handler. All other TPC failures are returned unchanged.

## State and Persistence Behavior

The wrapper owns one heap-allocated `CopyJob *pJob` at a time. It shares the base job ID, property list, and results list with the delegated job. No state is persisted outside those result properties.

## Dependencies and Integration Points

It integrates `CopyJob`, `ThirdPartyCopyJob`, `ClassicCopyJob`, `PropertyList`, copy progress handlers, logging, default environment, and status codes. It is selected by copy-process configuration when TPC-first behavior is requested.

## Risks and Edge Cases

Fallback is intentionally narrow. Authentication failures, checksum failures, destination open failures that are not normalized to `errNotSupported`, and most protocol errors do not fall back. Reusing the same property and result lists means partial TPC side effects may be visible to the classic job unless other code clears them.

## Test Signals

Tests should inject TPC success, `errNotSupported`, `errOperationExpired`, and unrelated errors, verifying which path runs and that progress/results are forwarded consistently.
