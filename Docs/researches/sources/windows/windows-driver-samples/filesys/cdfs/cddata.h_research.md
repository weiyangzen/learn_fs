# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cddata.h

## Purpose

`cddata.h` declares CDFS global variables/constants and debug/sanity assertion macros for validating CDFS objects and resource ownership.

## Main Contents

- External globals:
  - `CdData`
  - `CdFastIoDispatch`
  - reserved directory-name arrays/strings
  - descriptor ID strings
  - audio label and pseudo filename metadata
  - Joliet escape sequences
  - RIFF/XA header templates
  - optional `CdTelemetryData`

- Residual reference constants:
  - `CDFS_RESIDUAL_REFERENCE`
  - `CDFS_RESIDUAL_USER_REFERENCE`
  - Account for mounted volume, DASD FCB, root index FCB/internal stream, and path table FCB/internal stream.

- Sanity assertion macros under `CD_SANITY`:
  - Node type validation for VCB, FCB, FCB nonpaged, CCB, IRP context, IRP, file object.
  - Resource ownership checks for CdData, VCB, FCB, and file resources.
  - Mutex ownership checks for VCB/FCB locks.
  - `CD_SANITY` is enabled for `DBG` builds.

- Retail/non-sanity versions:
  - Assertion macros compile to no-ops.
  - `DebugBreakOnStatus` also no-ops.

## Integration

Included through `cdprocs.h`, this header gives every CDFS module a shared view of global data and debug validation. The macros are used heavily in allocation, cache, cleanup, dispatch, resource, and structure support code.

## Risk Notes

- The assertion layer catches structural misuse only in sanity/debug builds.
- Retail builds rely on normal code paths and NTSTATUS exception handling, not these assertions.
- The `ASSERT_FCB` macro accepts data, index, and path-table node types, matching the unioned FCB layout in `cdstruc.h`.
