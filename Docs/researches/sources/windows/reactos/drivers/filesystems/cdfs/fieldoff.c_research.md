# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fieldoff.c

## Purpose

`fieldoff.c` is a diagnostic/layout utility, not a filesystem runtime path. It includes `cdprocs.h` and prints field offsets and field sizes for the major CDFS in-memory and on-disk structures.

## Main Behavior

The file defines:

- `doit(a,b)`: prints the record type name, `FIELD_OFFSET(a,b)`, `sizeof(d.b)`, and field name.
- `main`: instantiates local variables of many CDFS structure types and invokes `doit` for each important field.

The output begins with:

`<Record> <offset> <size> <field>`

Then it prints grouped layout tables separated by blank lines.

## Structures Covered

The utility reports layout for:

- Mapping/name structures: `CD_MCB`, `CD_MCB_ENTRY`, `CD_NAME`, `NAME_LINK`, `PREFIX_ENTRY`.
- Global/volume structures: `CD_DATA`, `VCB`, `VOLUME_DEVICE_OBJECT`.
- FCB and CCB structures: `FCB_DATA`, `FCB_INDEX`, `FCB_NONPAGED`, `FCB`, `CCB`.
- Request and thread structures: `IRP_CONTEXT`, `IRP_CONTEXT_LITE`, `CD_IO_CONTEXT`, `THREAD_CONTEXT`.
- Path/dirent enumeration structures: `PATH_ENUM_CONTEXT`, `PATH_ENTRY`, `COMPOUND_PATH_ENTRY`, `DIRENT_ENUM_CONTEXT`, `DIRENT`, `COMPOUND_DIRENT`, `FILE_ENUM_CONTEXT`.
- CD-XA/media headers: `RIFF_HEADER`, `AUDIO_PLAY_HEADER`.
- Raw ISO/HSG structures: `RAW_ISO_VD`, `RAW_HSG_VD`, `RAW_DIRENT`, `RAW_PATH_ISO`, `RAW_PATH_HSG`, `SYSTEM_USE_XA`.

## Dependencies

It depends on all relevant CDFS type definitions being visible through `cdprocs.h`, and on `FIELD_OFFSET` being available. It also includes `<stdio.h>`, making it a host-style console program rather than kernel-driver code.

## Research Notes

This utility is useful when comparing ReactOS/Microsoft-derived structure packing, validating ABI-sensitive offsets, or debugging generated structure documentation. It uses old-style K&R `main(argc, argv)` parameters and does not consume its arguments.
