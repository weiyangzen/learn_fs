# sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.cc

## Purpose

This implementation provides the string conversion logic for the lightweight `XrdCl::Status` type. It translates internal XrdCl error codes and optional errno/XRootD protocol error numbers into operator-readable messages.

## Important APIs, Types, and Functions

The private `ErrorMap errors[]` table maps XrdCl error constants such as `errSocketTimeout`, `errAuthFailed`, `errCheckSumError`, and `errTlsError` to short messages. `GetErrorMessage` performs a linear lookup and falls back to "Unknown error code". `Status::ToString()` formats success, nonfatal error, and fatal error prefixes and appends decoded OS/protocol errors.

## Control Flow

`ToString` first checks `IsOK()`. Success returns `[SUCCESS]` plus `Continue` or `Retry` when the status code is `suContinue` or `suRetry`. Error statuses are prefixed with `[FATAL]` or `[ERROR]`, then the mapped error text. If `errNo` is at or above `kXR_ArgInvalid`, the code treats it as an XRootD protocol error and converts through `XProtocol::toErrno`; otherwise nonzero values are passed directly to `XrdSysE2T`.

## State and Persistence Behavior

The file has only static read-only mapping data. It does not persist state or mutate global configuration.

## Dependencies and Integration Points

It depends on `XrdClStatus.hh`, `XrdSysE2T` for errno text, and `XProtocol` constants/conversion. It is a common diagnostic path for many client components that return `Status`.

## Risks and Edge Cases

The mapping is manually maintained; new error constants can stringify as unknown if this table is not updated. The `errNo >= kXR_ArgInvalid` heuristic is explicitly compensating for inconsistent use of protocol errors versus errno, so boundary regressions can produce misleading text. Success with `suPartial`, `suAlreadyDone`, or other success hints prints only `[SUCCESS]`.

## Test Signals

Tests should cover representative generic, socket, auth, redirect, checksum, and TLS errors; fatal versus nonfatal prefixes; success hints; unknown codes; and errno/protocol conversion behavior.
