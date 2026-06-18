# File Research: sources/os/linux/linux-stable/fs/ntfs/layout.h

## Summary
Defines NTFS on-disk structures, constants, magic values, flags, indexes, security formats, quota records, reparse records, and extended-attribute records. This is the central schema header used when parsing or constructing NTFS metadata.

## Main Contents
- Boot-sector and BIOS parameter block structures.
- NTFS record magic values and helpers for `FILE`, `INDX`, `RSTR`, `RCRD`, `CHKD`, `BAAD`, `HOLE`, and empty records.
- Common multi-sector-transfer protected record header.
- System MFT record numbers and MFT reference packing/unpacking helpers.
- Current and old MFT record headers.
- Attribute type codes, attribute definition entries, attribute flags, resident/non-resident `struct attr_record`, and compression model notes.
- Standard information, attribute-list, file-name, GUID, and object-ID structures.
- Security identifiers, ACE/ACL/security descriptor structures, access masks, inheritance flags, and descriptor control flags.
- `$Secure` index keys, volume information flags, index headers/root/block/entry structures.
- Reparse, quota, EA-information, and packed EA structures.

## Important Behavior
The header is declarative but encodes many invariants used by parser code: packed little-endian layout, 8-byte alignment requirements for many variable records, MFT references as 48-bit record numbers plus 16-bit sequence numbers, update sequence array limits within the first 512-byte sector, and index entry trailing VCN placement.

Attribute records distinguish resident values embedded in the MFT record from non-resident values described by mapping pairs and VCN ranges. File and directory names are represented by resident `$FILE_NAME` attributes and directory index entries. Security descriptors are de-duplicated in `$Secure` through `$SII` and `$SDH` indexes.

## Cross-File Role
`logfile.h` and `logfile.c` use the record magic and common record protection definitions. Inode, attribute, index, MFT, directory, security, reparse, and EA code depend on this header for exact on-disk field offsets and flag values.

## Risks
Any drift between these packed structures and NTFS disk format corrupts parsing or writeback. Many structures contain variable-length tails, so callers must bounds-check lengths, offsets, alignment, and endian conversion before dereferencing embedded data.
