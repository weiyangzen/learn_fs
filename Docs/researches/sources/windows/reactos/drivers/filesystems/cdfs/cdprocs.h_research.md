# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cdprocs.h

## Purpose

`cdprocs.h` is the central internal interface header for CDFS. It includes platform headers and CDFS structure headers, defines pool tags/macros, and declares or macro-defines almost every cross-file helper used by the filesystem.

## Key Contents

- Includes:
  - NT filesystem/storage headers.
  - ReactOS SEH support via `<pseh/pseh2.h>`.
  - `nodetype.h`, `cd.h`, `cdstruc.h`, and `cddata.h`.
  - Optional telemetry headers.

- ReactOS compatibility:
  - Downgrades newer NX pool and MDL flags to older equivalents.
  - Adds GCC/static-inline annotations for functions that would otherwise conflict.
  - Uses ReactOS SEH macros in `try_leave`.

- Pool tags:
  - Tags for CCBs, TOC buffers, dirent names, enum expressions, FCB variants, I/O buffers, IRP contexts, MCB arrays, prefix entries, path-table buffers, volume descriptors, VPBs, etc.

- Access checks:
  - `CdIllegalFcbAccess` rejects write/delete/security-modifying access for normal readonly CDFS opens, with special casing for volume opens.

- Allocation/cache/device I/O declarations:
  - Logical allocation lookup/update/truncation.
  - Internal stream creation/deletion.
  - MDL completion and purge.
  - Noncached reads including XA reads.
  - raw sector reads and device control helpers.
  - user-buffer mapping and locking macros.

- Directory/path/name support:
  - Dirent lookup, update, search, cleanup, and file enumeration helpers.
  - Path-table lookup/search/update helpers.
  - Prefix-table insert/remove/find.
  - Name conversion, endian conversion, upcasing, dissection, legal-name checks, 8.3 generation, expression matching, and full comparisons.

- File-object contract:
  - Defines `TYPE_OF_OPEN`:
    - `UnopenedFileObject`
    - `StreamFileOpen`
    - `UserVolumeOpen`
    - `UserDirectoryOpen`
    - `UserFileOpen`
  - Declares `CdSetFileObject`, `CdDecodeFileObject`, and `CdFastDecodeFileObject`.

- Synchronization:
  - Declares `CdAcquireResource`.
  - Provides macros for acquiring/releasing CdData, VCBs, all files, individual file resources, FCB resources, and cache resources.
  - Provides fast-mutex lock/unlock macros for CdData, VCB, and recursive FCB locking.
  - Defines `TYPE_OF_ACQUIRE`.

- Structure lifecycle:
  - VCB initialization/update/delete.
  - FCB creation/initialization from path entries or file contexts.
  - CCB creation/delete.
  - file-lock creation/delete.
  - IRP context create/cleanup/stack initialization.
  - teardown routines and reference/cleanup count macros.
  - FCB table lookup and TOC processing.

- Verification/work queue:
  - Verify-required handling, dismount checks, marking verify flags, VCB/Fcb operation verification.
  - FSD post/prepost and oplock completion routines.

- Dispatch/exception/fast I/O:
  - Prototypes for `CdFsdDispatch`, `CdExceptionFilter`, `CdProcessException`, `CdCompleteRequest`, and `CdSetThreadContext`.
  - Inline `CdRaiseStatusEx` for non-`CD_SANITY` builds.
  - Fast I/O entry declarations.
  - Common major-function worker declarations for create, close, read, write, info, volume info, dir control, FS control, device control, lock control, cleanup, PnP, and shutdown.

- Utility macros:
  - pointer arithmetic
  - word/long/quad alignment
  - sector/block conversions
  - unaligned copy and endian swap helpers
  - `CdIsFastIoPossible`
  - `CanFsdWait`
  - safe pool free wrapper

- Optional telemetry:
  - provider declaration, initialization/mount hooks, stack guard, and no-op macros when telemetry is disabled.

## Dependencies and Interactions

- This header binds the entire CDFS module set together; every `.c` file in this group includes it directly or indirectly.
- It depends on `cdstruc.h` for concrete structure layouts and `cddata.h` for global declarations/assertions.
- Many macros assume caller-held resources or global critical region state, as indicated by SAL annotations.
- Several macros mutate VCB/FCB counts directly and require the VCB fast mutex.

## Behavioral Notes

- The file mixes declarations and behavior-heavy macros. Changing a macro here can alter locking, exception, or memory semantics across the whole driver.
- `CdIsFastIoPossible` encodes the fast-I/O policy: mounted volume, compatible oplock state, and file-lock state.
- `CdRaiseStatus` and `CdNormalizeAndRaiseStatus` capture source file ID and line into the IRP context before raising.
- ReactOS compatibility comments identify places where upstream Windows CDFS code needed GCC or kernel-version adaptation.
