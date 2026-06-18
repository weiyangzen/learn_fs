# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.cc

## Purpose
Implements the base cache IO adapter that wraps an upstream `XrdOucCacheIO`, exposes common path/location/update behavior, and implements delayed detach scheduling shared by concrete cache IO types.

## Important APIs, Types, and Functions
- `IO::IO()` stores cache reference, trace id, active read counter, upstream IO pointer, and read sequence id.
- `Update()` atomically replaces the upstream IO, refreshes remote location, and logs the new source location.
- `SetInput()`/`GetInput()` manage the atomic input pointer.
- `GetFilename()` converts the upstream URL path into a local filename path via `XrdCl::URL`.
- `Detach()` finalizes immediately when `ioActive()` is false or schedules a nested `FutureDetach` job that polls with exponential backoff up to 120 seconds.

## Control Flow
Concrete `IO` subclasses implement `ioActive()` and `DetachFinalize()`. `Detach()` asks whether reads, prefetches, or blocks still need the object. If not active, it calls finalization and returns true. If active, it schedules `FutureDetach`, returns false, and the job repeatedly rechecks activity before finalizing and invoking `DetachDone()`.

## State and Persistence Behavior
No persistent state is owned. Transient state includes the upstream IO pointer, active read request counter, sequence ids, attach/detach state fields used by `File`, prefetch permissions, and error/incomplete-read counters for diagnostics.

## Dependencies and Integration Points
Depends on `XrdPfcIO.hh`, trace macros, `XrdCl::URL`, `Cache::schedP`, and `XrdJob`. Concrete integrations are `IOFile` and `IOFileBlock`, both of which delegate actual cache state to `File`.

## Risks and Test Signals
Risks include lifetime of the detach callback captured by `FutureDetach`, polling delay during shutdown, and upstream IO replacement while reads are active. Tests should cover immediate detach, delayed detach with active reads, Update during an open file, and callback completion exactly once.
