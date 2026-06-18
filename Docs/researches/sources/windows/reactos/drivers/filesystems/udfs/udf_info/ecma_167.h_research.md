# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/ecma_167.h

## Purpose

`ecma_167.h` defines packed C structures and constants for ECMA-167/UDF on-disk descriptors. It is the schema layer used by UDFS parsing, allocation, directory indexing, volume recognition, and file-entry handling.

## Packing And Primitive Types

- Defines `dstring` as `uint8`.
- Defines compression IDs `UDF_COMP_ID_8` and `UDF_COMP_ID_16`.
- Uses `#pragma pack(push, 1)` / `#pragma pack(pop)` so on-disk descriptors match byte layout.

## Common Descriptor Types

The header defines:

- `charspec`
- `timestamp` / `UDF_TIME_STAMP`
- `EntityID` / `regid`
- volume structure descriptors and standard identifiers (`BEA01`, `NSR02`, `NSR03`, `TEA01`, etc.)
- `EXTENT_AD` / `extent_ad` / `EXTENT_MAP`
- descriptor `tag` / `DESC_TAG`
- tag identifiers for volume and file descriptors

## Volume And Partition Descriptors

Structures include:

- `BootDesc`
- `PrimaryVolDesc`
- `AnchorVolDescPtr`
- `VolDescPtr`
- `ImpUseVolDesc`
- `PartitionDesc`
- `LogicalVolDesc`
- generic/type 1/type 2 partition maps
- `UNALLOC_SPACE_DESC`
- `TerminatingDesc`
- `GenericDesc`
- `LogicalVolIntegrityDesc`

Constants cover partition flags, partition contents, access types, partition map types, integrity types, and maximum known VDS partition count.

## File And Allocation Descriptors

The header defines:

- `lb_addr`
- extent interpretation constants:
  - `EXTENT_RECORDED_ALLOCATED`
  - `EXTENT_NOT_RECORDED_ALLOCATED`
  - `EXTENT_NOT_RECORDED_NOT_ALLOCATED`
  - `EXTENT_NEXT_EXTENT_ALLOCDESC`
- `long_ad`, `SHORT_AD`, and `EXT_AD`
- `FILE_SET_DESC`
- `PARTITION_HEADER_DESC`
- `FILE_IDENT_DESC`
- `ALLOC_EXT_DESC`
- `icbtag`
- `IndirectEntry`
- `TerminalEntry`
- `FILE_ENTRY`
- `EXTENDED_FILE_ENTRY`
- `LogicalVolHeaderDesc`
- `PathComponent`

It also defines file characteristics, ICB file types, allocation descriptor type flags, ICB flags, file permissions, record formats, and path component types.

## Extended Attributes And Bitmaps

Structures include:

- `ExtendedAttrHeaderDesc`
- `GenericAttrFormat`
- `CharSetAttrFormat`
- `AlternatePermissionsExtendedAttr`
- `FileTimesExtendedAttr`
- `InfoTimesExtendedAttr`
- `DeviceSpecificationExtendedAttr`
- `ImpUseExtendedAttr`
- `AppUseExtendedAttr`
- `UnallocatedSpaceEntry`
- `SPACE_BITMAP_DESC`
- `PartitionIntegrityEntry`

Constants define known extended attribute type IDs and file-time existence bits.

## Integration

This header is consumed throughout `udf_info` code. For this group specifically:

- `dirtree.cpp` uses `FILE_IDENT_DESC`, `tag`, file characteristics, `lb_addr`, and descriptor lengths.
- `alloc.cpp` uses `EXTENT_AD`, `EXTENT_MAP`, `lb_addr`, and extent type constants.
- higher-level file and volume code use the volume, partition, file set, and file-entry structures to parse UDF media.

## Notable Details

- Flexible trailing arrays are represented as comments rather than C flexible-array members, so callers must do manual pointer arithmetic and length validation.
- All descriptors are packed; using these structures directly on unaligned buffers requires architecture/compiler care.
- The header is schema-only: it does not validate CRCs, tag checksums, descriptor lengths, or media bounds by itself.
