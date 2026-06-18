# sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.hh

## Purpose

This header declares `ClassicCopyJob`, the concrete `CopyJob` implementation for client-mediated copies. It is the normal fallback path when third-party copy is disabled or unavailable.

## Important APIs, types, and functions

The constructor accepts a job id, job property list, and job result list and forwards common initialization through `CopyJob`.

`Run(CopyProgressHandler*)` performs the copy and returns an `XRootDStatus`. `GetResult()` exposes the last stored result status.

Private helpers `SourceError` and `DestinationError` append `(source)` or `(destination)` to error messages and store the status as the final result. `SetResult` constructs and stores a final `XRootDStatus` from arbitrary constructor arguments.

## Control flow

`CopyProcess` creates `ClassicCopyJob` during `Prepare` for non-TPC jobs, then `QueuedCopyJob` calls `Run`. The implementation uses `SetResult`/source/destination error helpers for all terminal outcomes so `CopyProcess` can read the status from the result property list.

## State and persistence behavior

The class stores only `XRootDStatus result` in addition to inherited property/result pointers and URLs. Durable state changes happen in the `.cc` implementation by writing destination files or ZIP archives.

## Dependencies and integration points

The header depends on `XrdClCopyProcess.hh` and `XrdClCopyJob.hh`. It integrates with `CopyProcess`, `TPFallBackCopyJob`, `xrdcp`, and monitor/progress handling.

## Risks and edge cases

`SourceError` and `DestinationError` mutate the incoming status error message before storing it, which may surprise callers that reuse the same `XRootDStatus` object after passing it in. The result is separate from `pResults["status"]`; the implementation must keep both consistent at process level.

## Test signals

Tests should verify source/destination error labeling, result propagation, and interaction with `CopyProcess` retries.
