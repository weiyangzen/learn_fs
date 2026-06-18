# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.hh

## Purpose

`XrdRmcData.hh` declares the per-I/O-object cache wrapper that presents `XrdOucCacheIO` methods while routing reads, writes, truncation, and prereads through `XrdRmcReal`.

## Important APIs, Types, And Functions

- Public overrides include `Detach()`, `FSize()`, `Path()`, `Preread()`, `Preread(aprParms&)`, `Preread(Offs, rLen, Opts)`, `Read()`, `Sync()`, `Trunc()`, and `Write()`.
- Static `setAPR()` normalizes automatic preread parameters.
- Private `MrSw` RAII helper manages optional multiple-reader/single-writer locks.
- Private fields store stats, locks, cache pointer, underlying I/O pointer, virtual segment namespace, geometry, flags, and preread queue/ring state.

## Control Flow

The declaration shows that `XrdRmcData` is constructed only by `XrdRmcReal` and self-deletes through `Detach()`. Public `Sync()` is a no-op because the implementation is write-through.

## State And Persistence

Per-instance state covers file statistics and preread scheduling. There is no persistent storage; `Statistics` is merged into the parent cache at detach.

## Dependencies And Integration Points

It includes `XrdOucCache.hh`, `XrdRmcReal.hh`, `XrdSysPthread.hh`, and `XrdSysXSLock.hh`. It is a friend-level collaborator of `XrdRmcReal` through the parent class interfaces.

## Risks And Edge Cases

- Destructor is private and empty, so lifetime must follow the `Detach()` protocol.
- `Sync()` always returns success, which is correct for write-through but could surprise callers expecting underlying sync behavior.
- Many preread constants are fixed in the class, making tuning impossible without code changes.

## Test Signals

Compile tests should treat it as an `XrdOucCacheIO`. Runtime tests should verify caller-visible `Path`, `FSize`, `Sync`, and lifecycle semantics through `XrdRmcReal::Attach()`.
