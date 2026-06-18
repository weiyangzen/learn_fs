# File Research: sources/local-fs/jfsutils/fsck/fsckea.c

## Purpose
Validates the byte-level structure of a JFS extended attribute FEALIST used by fsck when checking inline and extent-backed extended attributes.

## Main Elements
- `FEA_SIZE(ea)`: computes one full FEA record length from little-endian value length, name length, null terminator, and fixed `struct FEA` header.
- `NEXT_FEA(ea)`: advances to the next FEA record by `FEA_SIZE()`.
- `GEA_SIZE()` / `NEXT_GEA()`: analogous get-EA-list helpers, defined here but unused in this file.
- `jfs_ValidateFEAList()`: validates the list byte count and each variable-length FEA record.

## Control Flow
`jfs_ValidateFEAList()` reads `pfeal->cbList` as little-endian, requires it to match the caller-supplied buffer size, subtracts the list length field, and accepts an otherwise empty list. It then walks records until no bytes remain. For each record it rejects reserved `fEA` flag bits, rejects headers that do not fit in the remaining bytes, computes the record size, advances to the next record, and reports inconsistency if the record extends beyond the remaining list bytes. On overrun, it stores the error offset in `*poError`.

## Dependencies And Integration
Declared through `xfsck.h` and called from `fsckino.c` during EA validation. Inline EAs are validated directly from the inode’s inline EA area after DXD bounds checks. Extent-backed EAs are first validated as extents, read into fsck’s EA buffer, and then passed here with the EA byte size from the inode DXD.

## Behavioral Notes
The validator checks list framing and reserved flag bits only. It does not validate EA name character sets, semantic name rules, duplicate names, value content, or alignment beyond what is implied by the packed record sizes.

## Risk Notes
The function relies on the caller to provide a buffer at least as large as `size` and on prior inode/DXD validation to ensure that `size` is meaningful. It is intentionally small, but because FEA records are variable-length on-disk data, integer sizing and remaining-byte checks are the key correctness boundary.
