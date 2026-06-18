# sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.hh

## Purpose

This header defines the compact status vocabulary used throughout older XrdCl code: status severity bits, success subcodes, error-code ranges, and the `Status` structure.

## Important APIs, Types, and Functions

Constants define severity (`stOK`, `stError`, `stFatal`), success hints (`suDone`, `suRetry`, `suPartial`, and others), generic errors, socket errors, postmaster errors, XRootD protocol errors, and query/redirect response errors. `Status` stores `status`, `code`, and `errNo`; exposes `IsError`, `IsFatal`, `IsOK`, `GetShellCode`, `IsSocketError`, and `ToString`.

## Control Flow

Callers construct `Status` with defaults for success or with an error severity and code. `IsError` tests the error bit; `IsFatal` tests the fatal bit; `GetShellCode` collapses grouped error ranges into shell exit values by returning `(code / 100) + 50`.

## State and Persistence Behavior

`Status` is a plain value type with no ownership, dynamic allocation, or persistence. It is intended to move through call returns and callbacks.

## Dependencies and Integration Points

The header depends only on C++ standard headers and is included by transport, stream, URL, task, and utility code. Many newer APIs in this tree use the richer `XRootDStatus`, but the same constants and semantic categories are shared.

## Risks and Edge Cases

The severity encoding is bit-based and easy to misuse if callers compare exact values instead of using helpers. `IsFatal()` uses `(status & 0x0002) & stFatal`, which works for current constants but is less clear than checking the fatal bit directly. Adding new error groups affects shell-code behavior.

## Test Signals

Useful tests validate bit semantics, shell-code grouping, socket-code detection, default OK construction, and stringification through `Status.cc`.
