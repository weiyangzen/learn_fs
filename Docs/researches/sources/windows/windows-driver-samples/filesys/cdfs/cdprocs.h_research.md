# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cdprocs.h

## Purpose

`cdprocs.h` is the central CDFS private interface header. It includes NT/storage headers and CDFS structure/data headers, defines allocation tags and utility macros, declares cross-module routines, and supplies inline helpers for synchronization, buffer handling, exceptions, alignment, telemetry, and fast-I/O state.

## Major Areas

- Includes:
  - `ntifs.h`, CD-ROM/disk/SCSI IOCTL headers.
  - `nodetype.h`, `Cd.h`, `CdStruc.h`, `CdData.h`.
  - Optional telemetry headers.

- Pool tags:
  - Tags for CCBs, TOCs, dirent names, FCBs, file names, I/O contexts, IRP contexts, MCB arrays, prefix/path structures, volume descriptors, VPBs, and more.

- Access checks:
  - `CdIllegalFcbAccess` rejects write/delete/DAC style access on read-only CDFS objects, with a narrower rule for volume opens.

- Allocation support declarations:
  - `CdLookupAllocation`
  - `CdAddAllocationFromDirent`
  - `CdAddInitialAllocation`
  - `CdTruncateAllocation`
  - `CdInitializeMcb`
  - `CdUninitializeMcb`

- Cache support declarations/macros:
  - Internal stream create/delete.
  - MDL completion.
  - Volume purge.
  - `CdVerifyOrCreateDirStreamFile`.
  - `CdUnpinData`.

- Device I/O declarations:
  - Noncached reads, XA reads, volume DASD writes, sector reads, MDL creation, device control helpers, IRP hijack/flush.

- Dirent and file enumeration:
  - Dirent lookup/update routines.
  - File/directory find routines.
  - Initialization/cleanup macros for `FILE_ENUM_CONTEXT`, `DIRENT`, and `DIRENT_ENUM_CONTEXT`.

- File-object support:
  - `TYPE_OF_OPEN` enum.
  - `CdSetFileObject`, `CdDecodeFileObject`, `CdFastDecodeFileObject`.

- Name support:
  - CD name conversion, upcasing, dissection, legality checks, 8.3 generation, wildcard matching, full comparison.

- Filesystem control/path/prefix:
  - Volume lock/unlock internals.
  - Path table enumeration and lookup.
  - Prefix insert/remove/find.

- Synchronization:
  - Resource acquisition API and macros for CdData, VCB, file, and FCB resources.
  - Fast mutex lock/unlock macros for CdData, VCB, and recursively-lockable FCB mutexes.
  - Cache sector resource helpers.
  - Oplock location abstraction for pre/post Win8 layouts.

- Cache/section callbacks:
  - No-op volume callbacks.
  - cache acquire/release callbacks.
  - FS filter acquire callback for section creation.
  - section release callback.

- Structure lifetime:
  - VCB initialization/update/delete.
  - FCB create/initialize.
  - CCB create/delete.
  - file lock create/delete.
  - IRP context create/cleanup/stack initialization.
  - teardown.
  - reference/cleanup count macros.
  - FCB table lookup/iteration.
  - TOC processing.

- Verification:
  - verify, dismount, mark-device-for-verify, VCB/FCB operation verification.
  - raw-device status classification.

- Work queue:
  - request posting, pre-post, oplock completion, FSP dispatch, close worker.

- Utility macros:
  - pointer arithmetic, word/long/quad alignment.
  - sector/block alignment and conversion.
  - unaligned copy and endian swap helpers.
  - LBN-to-MSF declaration.
  - top-level context restore.
  - `CanFsdWait`.
  - `CdIsFastIoPossible`.
  - `try_return`/`try_leave`.
  - safe pool free.

- Dispatch/common operation declarations:
  - `CdFsdDispatch`
  - exception/filter/completion routines
  - all `CdCommon*` operation entry points.

- Telemetry:
  - Optional TraceLogging provider declarations.
  - stack-space guard before telemetry calls.
  - mount telemetry safe wrapper.

## Integration

Every CDFS implementation file includes this header. It defines the effective private ABI between modules such as allocation, cache, create, close, read, dir control, FS control, verification, path/name support, and structure management.

## Risk Notes

- Many helpers are macros with side effects, so argument evaluation and lock state must be correct.
- Locking order is embodied in macros and comments but enforced mostly by assertions.
- The header mixes declarations with inline logic; changes here have broad driver-wide blast radius.
- The FCB recursive lock macro relies on `FcbLockThread`/`FcbLockCount` consistency.
- Telemetry is guarded for stack usage because TraceLogging can consume significant kernel stack.
