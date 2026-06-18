# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_volume.h

## Role

Defines UDF on-disk volume, descriptor, file-entry, allocation, extended-attribute, partition-map, sparing, and path-component structures shared by UDF parsing and formatting code.

## Key Definitions

- UDF revision constants: `UDF_102`, `UDF_150`, `UDF_200`.
- Identifier strings for UDF domain, logical-volume info, virtual/sparable partitions, VAT, sparing tables, free EA space, OS/2/Mac attributes, and copy-management metadata.
- Endian helpers `SWAP_16`, `SWAP_32`, `SWAP_64`, `GET_32`; BCD conversion helpers; anchor descriptor location/length constants.
- Common descriptor primitives: `tag_t`, `charspec_t`, `regid_t`, logical block address macros, `extent_ad_t`, `short_ad_t`, `long_ad_t`, and UDF timestamp `tstamp_t`.

## Disk Format Structures

The file declares descriptor layouts for:
- Volume descriptors: primary volume, anchor pointer, volume descriptor pointer, implementation-use descriptor, partition descriptor, logical volume descriptor, unallocated-space descriptor, terminating descriptor, logical volume integrity descriptor, and file-set descriptor.
- File and allocation objects: `file_id`, `alloc_ext_desc`, `indirect_entry`, `term_entry`, `file_entry`, extended-attribute header, unallocated-space entry, space bitmap, and partition integrity descriptor.
- Extended attributes: generic `attr_hdr`, device-special EA, file-times EA, implementation-use EA, CGMS/copy-management overlay, and free-space overlay.
- Volume recognition and mappings: `nsr_desc`, type-1 and type-2 partition maps, sparing-table entries/table, and symlink/path components.

## ABI Notes

Many structures mirror exact UDF byte layouts and use fixed comments for offsets. `FID_LEN()` accounts for implementation-use length, identifier length, compression ID, and 4-byte alignment. The file deliberately encodes some fields as byte arrays or split macros to handle endian and packing constraints.

## Risk Notes

This is disk-format ABI. Field reordering, type-size changes, or alignment changes would break media compatibility. Consumers must apply `SWAP_*`/length macros consistently when parsing on big-endian systems.
