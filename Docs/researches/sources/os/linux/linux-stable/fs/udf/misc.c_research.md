# File Research: sources/os/linux/linux-stable/fs/udf/misc.c

## Summary
Provides UDF helper routines for extended attributes, descriptor tag validation, descriptor tag creation/update, and tag checksums.

## Main Responsibilities
- Adds and retrieves in-inode extended attributes from the file entry's `i_data` area.
- Creates an Extended Attribute Header Descriptor when adding the first EA.
- Maintains EA insertion ordering by attribute type ranges and adjusts implementation/application attribute offsets.
- Reads tagged UDF descriptors with location, checksum, version, and descriptor CRC validation.
- Updates descriptor tags after in-memory descriptor modifications.

## Important Behavior
`udf_read_tagged()` rejects invalid descriptor blocks early: invalid block number, failed read, tag location mismatch, checksum failure, unsupported descriptor version, oversized CRC length, or CRC mismatch.

`udf_add_extendedattr()` only supports inline EA storage and has a TODO for free EA space accounting. It may shift existing allocation descriptors when inserting an EA header or attribute.

## Risks
EA manipulation depends on correct `i_lenEAttr`, `i_lenAlloc`, and file-entry allocation offset accounting. Corruption in these fields can lead to rejected descriptors or misplaced inline allocation descriptors.
