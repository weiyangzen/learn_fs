# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.hh

## Purpose

`XrdXrootdPio` is the per-operation descriptor used by `XrdXrootdProtocol` to queue or resume parallel I/O. It records the protocol member function to resume, the `IOParms` for the file operation, and the stream id associated with the request.

## Important APIs, types, and functions

The public fields `Next`, `ResumePio`, `IO`, and `StreamID` form an intrusive queue node. `Alloc()`, `Recycle()`, `Clear()`, and `Set()` are the lifecycle helpers. `Set()` copies the resume member-function pointer, the `IOParms`, and two-byte stream id into the descriptor.

## Control flow

Protocol execution code allocates a small batch, fills entries with `Set()`, chains them through `Next`, and later invokes `ResumePio` through the owning protocol object. `Recycle()` returns descriptors to the global pool after `Cleanup()` dereferences any file objects attached through `IO.File`.

## State and persistence behavior

PIO descriptors are transient scheduling state only. The header deliberately stores raw pointers and a copied `IOParms` struct; reference management for `XrdXrootdFile` is handled by the caller, not by this type.

## Dependencies and integration points

The header depends on protocol types from `XProtocol/XPtypes.hh`, locking from `XrdSysPthread.hh`, and `XrdXrootdProtocol.hh` for `IOParms` and member-function pointer types. It is tightly integrated with bound streams, async/offloaded I/O, and protocol cleanup.

## Risks and edge cases

Because descriptors contain raw file pointers and member-function pointers, stale entries after recycle would be dangerous; `Clear()` is therefore part of the pool contract. The type has no copy prevention, so accidental by-value copies could duplicate ownership assumptions. `StreamID` is fixed at two bytes, matching the wire protocol.

## Test signals

Signals include verifying `Set()` preserves stream id and `IOParms`, `Clear()` resets every reused field, and cleanup paths recycle descriptors only after file reference counts have been decremented.
