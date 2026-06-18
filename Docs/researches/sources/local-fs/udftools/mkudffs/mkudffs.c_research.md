# File Research: sources/local-fs/udftools/mkudffs/mkudffs.c

## Role

Core UDF image construction support for `mkudffs`. This file owns initialization of `struct udf_disc`, UDF revision policy, physical-space partitioning, and construction of the major on-disk descriptor structures written by the formatter.

## Main Responsibilities

- Initializes a new UDF disc model with default descriptors, timestamps, UUID-like Volume Set Identifier prefix, descriptor lists, and default UDF revision 2.01.
- Applies UDF revision changes across domain identifiers, implementation identifiers, file entry policy, and default descriptor templates.
- Splits media into typed extents: boot/MBR area, VRS, anchors, main/reserve VDS, LVID, sparing table, sparing space, partition space, unallocated/reserved space.
- Creates descriptor payloads for MBR, Volume Recognition Sequence, anchors, partition space, file set, root directory, VDS descriptors, LVID, sparing tables, and VAT.
- Adds logical volume partition maps for type 1, type 2 sparable, and type 2 virtual partitions.
- Provides `dump_space()` and `write_disc()` traversal helpers over the extent list.

## Important Functions

- `udf_init_disc()` zeroes the disc, sets defaults, allocates default UDF descriptors, initializes descriptor string lengths, creates the initial `USPACE` extent, and calls `udf_set_version(0x0201)`.
- `udf_set_version()` accepts only UDF 1.01, 1.02, 1.50, 2.00, 2.01, 2.50, and 2.60. It toggles EFE support for UDF >= 2.00, sets NSR02/NSR03 partition content identifiers, and updates revision fields in active/default descriptor templates.
- `split_space()` is the formatter layout engine. It validates start/last blocks, reserves boot/VRS/anchor locations, calculates size requirements, lays out VDS/LVID/sparing/partition extents with alignment rules, updates LVID free/size tables, and removes temporary pre-start reservations.
- `setup_vrs()`, `setup_anchor()`, `setup_vds()`, and the `setup_*` descriptor helpers materialize logical extents into descriptor objects with correct tags and duplicate reserve descriptors when applicable.
- `setup_space()` creates unallocated/freed space bitmap or table entries inside partition space and updates partition header descriptor pointers.
- `setup_fileset()` and `setup_root()` allocate the FSD and root directory, optionally creating stream directory and non-allocatable-space metadata entries.
- `setup_vat()` builds either UDF 1.50 VAT with LV extension EA or UDF 2.00+ VAT header plus table, and records `disc->vat_block`.
- `add_type1_partition()`, `add_type2_sparable_partition()`, and `add_type2_virtual_partition()` append partition maps and resize LVID partition accounting arrays.

## Data Flow

`mkudffs/main.c` and `options.c` configure a `struct udf_disc`; this file turns that model into a linked list of typed extents with descriptor/data chains. `write_disc()` later delegates each extent to the configured write callback.

## Dependencies

- Local headers: `mkudffs.h`, `file.h`, `defaults.h`.
- Shared UDF helpers from `libudffs.h`: extent/list management, allocation helpers, endian conversion, string/CRC helpers through included headers.
- Linux geometry ioctl `HDIO_GETGEO` is used only for CHS fields when emitting an MBR.

## Notable Behaviors

- VAT media avoids the final anchor and has special closed-disc anchor/VAT alignment rules.
- Non-VAT media writes the final anchor at end-of-volume/session and may place a second anchor at end minus 256.
- Space bitmap partitions are rounded so the last bitmap byte is not partial, due to Windows `chkdsk` compatibility concerns.
- UDF 2.50+ is only partially supported in the wider tool; this file has VAT 2.00+ support but no metadata partition creation path for non-VAT media.
- Allocation failures and impossible layouts are fatal via `fprintf` plus `exit(1)`.

## Research Notes

This file is the main place to study if changing formatter layout, descriptor tagging, VAT emission, sparing support, or media alignment. It assumes the shared extent helpers keep the extent list sorted and split correctly.
