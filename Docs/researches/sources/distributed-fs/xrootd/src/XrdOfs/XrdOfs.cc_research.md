# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.cc

## Purpose

`XrdOfs.cc` is the primary implementation of the XRootD OFS layer: it adapts the `XrdSfsFileSystem`, `XrdSfsFile`, and `XrdSfsDirectory` interfaces to the configured `XrdOss` storage plugin, authorization plugin, CMS/finder services, event notification, POSC persistence-on-successful-close, third-party-copy, checksum, page read/write, and checkpoint support. It owns the ordinary runtime control flow for opens, reads, writes, metadata operations, redirects/stalls, and error conversion.

## Important APIs, Types, and Functions

- Globals: `OfsEroute`, `OfsTrace`, `OfsStats`, and `XrdOfsOss` are the error route, trace switch, stats collector, and active storage backend. `XrdOfs::dummyHandle`, `MaxDelay`, and `OSSDelay` provide shared handle/default delay state.
- Local helper `VerPgw()` validates page-write checksum vectors via `XrdOucPgrwUtils::csVer()` and reports offset-specific corruption.
- `XrdOfs::XrdOfs()` establishes defaults for modes, role, POSC, checksum, prepare, xattr, directory redirect, proxy, page-rw, and extended-error behavior.
- `XrdOfsDirectory::open()`, `nextEntry()`, `close()`, and `autoStat()` implement directory lifecycle against `XrdOssDF` directory objects with optional authorization and CMS locating.
- `XrdOfsFile::open()` is the central open/create path. It maps SFS flags to POSIX/OSS flags, authorizes create/read/update/TPC, consults `Finder`, manages POSC queue entries, creates/attaches `XrdOfsHandle`, opens `XrdOssDF`, initializes TPC destination state, sets compressed/raw I/O, emits events, and updates open statistics.
- `XrdOfsFile::close()` retires handles, tears down TPC, completes or unpersists POSC files, restores outstanding checkpoints, emits close events, and updates counters.
- `XrdOfsFile::checkpoint()` dispatches `cpCreate`, `cpDelete`, `cpQuery`, `cpRestore`, `cpTrunc`, and `cpWrite`; `CreateCKP()` chooses proxy-supplied checkpoint objects or local `XrdOfsChkPnt`.
- I/O methods include synchronous and AIO `read`, `write`, `readv`, `pgRead`, `pgWrite`, `sync`, `truncate`, `stat`, `getMmap`, `getCXinfo`, and clone calls. They funnel to `oh->Select()` and translate failures through `Emsg()`.
- Filesystem methods include `chksum`, `chmod`, `Connect`, `Disc`, `exists`, `getStats`, `mkdir`, `prepare`, `remove`, `rename`, two `stat` variants, and path-level `truncate`.
- Helpers `Emsg()`, `EmsgType()`, `fsError()`, `Forward()`, `Stall()`, `Unpersist()`, `WaitTime()`, `Split()`, `Fname()`, and `Reformat()` normalize protocol-visible responses and side effects.

## Control Flow

The open path first rejects reuse of an already-open `XrdOfsFile`, derives open/create/POSC/finder flags, optionally redirects TPC writes, and delegates location to CMS. Creates are authorized separately for normal create versus exclusive create; POSC creates are pre-entered into `poscQ`. After `XrdOfsOss->Create()` and `XrdOfsHandle::Alloc()`, existing active handles can be shared unless the request is a TPC writer. Otherwise a new `XrdOssDF` is opened, the handle is activated, fadvise may be issued for sequential I/O, events/statistics are emitted, and ownership transfers out of the RAII `OpenHelper`.

Read/write control flow is deliberately thin after open: it checks 32-bit offset limits, chooses raw or normal reads for compressed/raw I/O, maps page-rw to OSS-native `pgRead`/`pgWrite` when available or simulates it, and uses AIO only where the backend supports it. POSC writes and syncs are forced synchronous where errors must be detected before the file is made persistent.

Metadata operations all follow a common pattern: build `XrdOucEnv` from opaque/client data, authorize the operation, locate or forward via CMS if this node is remote, emit optional events, call the `XrdOss` operation, update `Balancer` or handle caches, then translate errors or special responses to SFS return codes.

## State and Persistence Behavior

The main state is held in `XrdOfsHandle` instances. Handles track active/inactive state, usage, writer/POSC mode, pending writes, first-write state, compression, and the selected `XrdOssDF`. `ocMutex` protects assignment of the per-file `oh` pointer and open/close transitions.

POSC is persistent state backed by `XrdOfsPoscq`. During create/open, paths can be entered into the POSC queue; on successful close the pending POSC bit is cleared with `Fchmod()`, the queue record is deleted, and the balancer is updated. On write/sync/close failures, `Emsg(..., posChk=true)` or close cleanup calls `Unpersist()`, which deletes the file or queue entry, emits removal/close notifications, and increments `numUnpsist`.

Checkpoint state is per `XrdOfsFile` through `myCKP` and `ckpBad`. Checkpoint failures set `ckpBad`, suppress additional checkpoint write/truncate operations, and may suppress backend access via `oh->Suppress()`. Close automatically attempts `myCKP->Restore()` before deleting the checkpoint object.

Statistics are kept in `OfsStats`, with some counters intentionally updated without locks for redirect/stall/error hot paths. Event state is external in `evsObject`; CMS state is external in `Finder`/`Balancer`.

## Dependencies and Integration Points

This file integrates with `XrdOss` for storage, `XrdCmsClient` for locate/prepare/forward/balancer updates, `XrdAccAuthorize` through the `AUTHORIZE` macro, `XrdOfsEvs` for notifications, `XrdOfsTPC` for third-party-copy source and destination flows, `XrdCks` for checksums, `XrdOfsChkPnt`/`XrdOucChkPnt` for checkpoints, `XrdOfsPoscq` for POSC, `XrdOucEnv` for opaque/environment metadata, and `XrdSfs` protocol return conventions. Proxy backends are detected through OSS features and environment and alter direct-open, checkpoint, checksum, and raw-I/O behavior.

## Risks and Edge Cases

- Open/close correctness depends on `XrdOfsHandle` locking discipline. Existing handles may be reused; TPC write requests are rejected on already-active targets.
- POSC failures intentionally delete data. Any incorrect `posChk` use or async path that hides write errors could cause unexpected unpersist behavior.
- `rename()` has an acknowledged race when emulating no-overwrite authorization by checking destination existence before rename.
- Checkpoint and POSC are mutually exclusive, but the interaction is spread between `CreateCKP()`, open modes, close cleanup, and error handling.
- Remote forwarding can return redirects, stalls, started responses, or errors from different layers; callers must not assume local POSIX semantics.
- `EmsgType()` maps `EBUSY` and `ETIMEDOUT` into stalls rather than hard errors, which is protocol-visible behavior.
- Page-write checksum verification is only simulated when OSS lacks page-rw support; native verification is delegated to the backend.

## Test Signals

Useful tests include create/open mode mapping with authorization combinations, POSC success and failure recovery, close-on-destructor behavior, TPC source/destination opens, Finder redirect/stall/error mapping, checksum `csSize/csGet/csCalc`, pgRead/pgWrite native versus simulated behavior, checkpoint create/write/truncate/restore/delete and failure suppression, first-write/close event delivery, and metadata operations with balancer updates. Fault-injection against `XrdOssDF` return codes should verify `Emsg`, `Stall`, and `fsError` conversions.
