# File Research: sources/windows/reactos/drivers/filesystems/udfs/protos.h

## Role

`protos.h` is the main cross-module prototype header for the ReactOS UDF filesystem driver. It declares dispatch entry points, common IRP handlers, Fast I/O callbacks, filesystem-control helpers, metadata/query/set helpers, security routines, verification/dismount functions, read/write helpers, and miscellaneous infrastructure APIs.

## Interface Coverage

The header groups prototypes by implementation file:

- `create.cpp`: create dispatch, common create, first-open/open-file, and FCB initialization.
- `cleanup.cpp` and `close.cpp`: cleanup/close dispatch, file-info chain cleanup, delayed close queue handling, and delayed close worker.
- `dircntrl.cpp`: directory control, query directory, and change notification.
- `devcntrl.cpp`: device control, completion, and query-path handling.
- `fastio.cpp`: Fast I/O read/write/query/device-control callbacks plus cache-manager acquire/release callbacks.
- `fileinfo.cpp`: query/set file information, rename, hardlink, file ID cache, allocation/EOF/disposition/basic/stream information helpers.
- `flush.cpp`: file, directory, and logical-volume flush operations and completion/break helpers.
- `fscntrl.cpp`: filesystem control, mount, volume lock/unlock/dismount, bitmap/retrieval pointer queries, statistics, path validation, eject waiter, VCB cleanup, and volume mounted/dirty checks.
- `lockctrl.cpp`: normal and Fast I/O byte-range locking APIs.
- `misc.cpp`: zones, exception handling, object/FCB/CCB/IRP-context lifecycle, posting, VCB init/release, registry/config parameters, EA rejection, resource helpers, and write-cache error handling.
- `namesup.cpp`: included through `namesup.h`.
- `pnp.cpp`: PnP dispatch.
- `read.cpp`: read dispatch, stack-overflow read posting, common read, buffer locking/unlocking, caller buffer lookup, and MDL completion.
- `SecurSup.cpp`: query/set security, ACL assignment/deassignment, security read/write, access checks.
- `Shutdown.cpp`, `Udf_dbg.cpp`, `UDFinit.cpp`, `verify.cpp`, `VolInfo.cpp`, and `write.cpp`: shutdown, debug resource wrappers, driver entry/init, verify/dismount comparison, volume information, write, deferred write, and cache purge/zero-data APIs.

## Compile-Time Shaping

The header uses build flags to expose or hide behavior:

- `UDF_READ_ONLY_BUILD` removes write/set-information/set-security/set-volume prototypes in several sections.
- `_WIN32_WINNT >= 0x0400` enables newer Fast I/O callback prototypes.
- `UDF_ENABLE_SECURITY` and `UDF_HANDLE_EAS` condition security/EA-related dispatch exposure elsewhere in the codebase.
- A large physical I/O prototype block is disabled under `#if 0`, but includes the active `UDFReadSectors` macro that chooses write-cache reads when available and falls back to `UDFTRead()`.

## Dependencies

`protos.h` includes `mem.h` and `namesup.h`, and depends on nearly all UDF driver types (`VCB`, `UDFFCB`, `UDFCCB`, `UDFIrpContext`, file-info structures, write-cache types) plus Windows kernel IRP, device, file object, security, Fast I/O, and cache manager types.

## Notable Risks

- Because this is a broad global prototype header, changes can ripple across almost every UDF compilation unit.
- It contains inline/macro behavior, not just declarations, including `UDFReleaseFCB`, `UDFRemoveFromDelayedQueue`, `UDFReadSectors`, and cache purge/zero-data aliases.
- Some declarations are inconsistent in style or type spelling, such as `extern OSSTATUS NTAPI UDFRead()` while the implementation returns `NTSTATUS`.
- Disabled prototype blocks preserve stale declarations and even malformed text, so enabling them would require cleanup.
