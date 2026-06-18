# File Research: sources/os/linux/linux-stable/fs/udf/ecma_167.h

## Summary
Packed ECMA-167 3rd edition on-disk structure and constant definitions used by the Linux UDF filesystem.

## Main Responsibilities
- Defines ECMA-167 primitive on-disk types: character specs, timestamps, entity identifiers, extent descriptors, descriptor tags, logical block addresses, and allocation descriptors.
- Defines descriptor tag IDs for volume descriptors, file-set descriptors, file identifiers, allocation extent descriptors, file entries, extended attributes, unallocated-space entries, space bitmaps, and extended file entries.
- Defines volume structures: VSD, boot descriptor, primary volume descriptor, anchor, partition descriptor, logical volume descriptor, partition maps, unallocated-space descriptor, terminating descriptor, and logical volume integrity descriptor.
- Defines file/directory structures: file set descriptor, partition header descriptor, file identifier descriptor, ICB tag, indirect/terminal entries, file entry, extended file entry, and allocation descriptors.
- Defines extended attribute structures and constants for charset, alternate permissions, times, device spec, implementation use, and application use.
- Defines extent type masks and allocation states used throughout UDF extent handling.

## Important Structures
- `struct tag`: common descriptor tag with identifier, version, checksum, serial, CRC, CRC length, and tag location.
- `struct fileIdentDesc`: variable-length directory entry descriptor.
- `struct icbtag`: ICB strategy, file type, parent location, and allocation descriptor flags.
- `struct fileEntry` / `struct extendedFileEntry`: core inode-on-disk formats.
- `struct short_ad`, `struct long_ad`, `struct ext_ad`: allocation descriptor formats.
- `struct logicalVolIntegrityDesc`: free-space and size tables used for volume integrity/accounting.

## Risks
This header is an on-disk format contract. All structs are packed and endian-annotated; layout drift would break media compatibility. Constants such as `EXT_TYPE_MASK`, `EXT_LENGTH_MASK`, and ICB allocation flags are directly interpreted by allocation, inode, directory, and superblock code.
