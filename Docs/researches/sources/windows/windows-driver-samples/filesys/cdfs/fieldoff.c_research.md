# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fieldoff.c

## Purpose

A standalone diagnostic/layout utility, not runtime filesystem-driver logic. It includes `CdProcs.h` and `stdio.h`, defines a `doit` macro, and prints structure field offsets and field sizes.

## Main Behavior

`main` prints a header and then instantiates many CDFS structure types on the stack solely so the macro can compute:

- structure name
- `FIELD_OFFSET(type, field)`
- `sizeof(d.field)`
- field name

The output format is:

`<Record>  <offset>  <size>  <field>`

## Covered Structures

The utility reports offsets for core CDFS structures, including:

- `CD_MCB`, `CD_MCB_ENTRY`
- `CD_NAME`, `NAME_LINK`, `PREFIX_ENTRY`
- `CD_DATA`
- `VCB`, `VOLUME_DEVICE_OBJECT`
- `FCB_DATA`, `FCB_INDEX`, `FCB_NONPAGED`, `FCB`
- `CCB`
- `IRP_CONTEXT`, `IRP_CONTEXT_LITE`, `CD_IO_CONTEXT`, `THREAD_CONTEXT`
- `PATH_ENUM_CONTEXT`, `PATH_ENTRY`, `COMPOUND_PATH_ENTRY`
- `DIRENT_ENUM_CONTEXT`, `DIRENT`, `COMPOUND_DIRENT`, `FILE_ENUM_CONTEXT`
- `RIFF_HEADER`, `AUDIO_PLAY_HEADER`
- `RAW_ISO_VD`, `RAW_HSG_VD`, `RAW_DIRENT`
- `RAW_PATH_ISO`, `RAW_PATH_HSG`
- `SYSTEM_USE_XA`

## Notes

The function is K&R-style C with `VOID __cdecl main(argc, argv)`. It does not use `argc` or `argv`. There is no mutation of driver state, no IRP handling, and no filesystem behavior. Its value is build/debug support for verifying binary layout expectations across CDFS internal and on-disk structures.
