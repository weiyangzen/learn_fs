# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.hh

## Purpose
Declares `XrdPfc::IO`, the abstract base class for proxy-cache `XrdOucCacheIO` adapters. It supplies common unsupported write/truncate behavior, source-path access, detach splitting, remote input management, read sequence ids, and shared counters.

## Important APIs, Types, and Functions
- Overrides `Path`, `Sync`, `Trunc`, `Write`, `Update`, and final `Detach`.
- Abstract `ioActive()` and `DetachFinalize()` define subclass-specific lifetime checks and destruction.
- `GetLocation()`, `GetTrace()`, `GetInput()`, `GetFilename()`, and `RefreshLocation()` expose upstream/cache context.
- `ReadReqRHCond` adapts `ReadReqRH` into a synchronous condition-variable callback.
- Friend relationship with `File` allows `File` to manage attach time, prefetch state, and detach flags under its own lock.

## Control Flow
Subclasses inherit the XRootD cache IO interface and implement read/stat behavior. Base `Detach()` centralizes delayed finalization so subclasses only answer whether active work remains and how to release their `File` references.

## State and Persistence Behavior
State is runtime-only: `m_io` points to the current upstream IO, `m_active_read_reqs` counts synchronous/asynchronous read operations, `m_read_seqid` tags logs, and detach/prefetch fields are managed by `File`. No disk state is written here.

## Dependencies and Integration Points
Depends on `XrdOucCache.hh`, `XrdSysRAtomic`, `XrdPfc.hh`, and `ReadReqRH` from `XrdPfcFile.hh` indirectly through include order. It is the common contract for `IOFile` and `IOFileBlock` and bridges XRootD cache APIs into PFC internals.

## Risks and Test Signals
Risks include abstract class coupling to `File` private state, atomic pointer assumptions, and unsupported write/truncate expectations. Tests should ensure write/truncate callers receive `-ENOTSUP`, sequence ids advance, and detach behavior is uniform across subclasses.
