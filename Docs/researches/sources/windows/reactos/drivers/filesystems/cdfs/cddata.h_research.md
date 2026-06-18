# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cddata.h

## Purpose

`cddata.h` declares global CDFS data and constants exported from `cddata.c`, plus assertion and locking verification macros used throughout the driver.

## Key Contents

- Extern globals:
  - `CdData`
  - `CdFastIoDispatch`
  - directory name arrays and `CdUnicodeDirectoryNames`
  - descriptor IDs `CdHsgId`, `CdIsoId`, `CdXaId`
  - audio label/name fields and audio dirent sizing values
  - Joliet escape array
  - RIFF/audio header templates
  - optional telemetry context

- Reference-count constants:
  - `CDFS_RESIDUAL_REFERENCE` is `6`.
  - `CDFS_RESIDUAL_USER_REFERENCE` is `3`.
  - Comments explain residual references for mounted VCB, volume DASD FCB, root index/internal stream, and path table/internal stream.

- Audio filename offsets:
  - `AUDIO_NAME_ONES_OFFSET`
  - `AUDIO_NAME_TENS_OFFSET`

- `CD_SANITY` assertion layer:
  - Structure assertions for VCB, FCB, FCB nonpaged, CCB, IRP context, IRP, and file object.
  - Resource ownership assertions for global data, VCB, FCB, file resources, and mutex-style VCB/FCB locks.
  - FCB assertions accept data, index, and path-table node types.
  - In non-sanity builds, these macros compile to `NOTHING`.

## Dependencies and Interactions

- This header assumes node type constants from `nodetype.h` and structures from `cdstruc.h` are already visible through `cdprocs.h`.
- Assertions are used heavily by cleanup, close, resource, and structure-management code.
- The residual reference constants are important to dismount/teardown logic in close and verify paths.

## Behavioral Notes

- In ReactOS/current configuration, `CD_SANITY` is not forcibly enabled; debug code contains a commented-out define.
- Non-sanity builds intentionally remove almost all assertion overhead.
- The header is declarative; the only “logic” is macro validation behavior.
