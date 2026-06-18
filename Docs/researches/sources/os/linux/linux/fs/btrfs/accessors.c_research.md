# File Research: sources/os/linux/linux/fs/btrfs/accessors.c

Purpose: Implements generic low-level read/write helpers for Btrfs on-disk metadata fields stored in `extent_buffer` folios.

Main behavior:
- Generates `btrfs_get_8/16/32/64()` and `btrfs_set_8/16/32/64()` with `DEFINE_BTRFS_SETGET_BITS`.
- Treats metadata item pointers as logical offsets into an extent buffer.
- Supports fields crossing folio boundaries, needed when metadata block size exceeds page size.
- Performs bounds checking against `eb->len`; violations are reported through `report_setget_bounds()`.
- Uses little-endian unaligned loads/stores for serialized fields.
- Implements `btrfs_node_key()` by reading a key from a node pointer slot via `read_eb_member`.

Important details:
- Cross-folio two-byte fields are copied byte by byte; wider fields use a small byte buffer and split copy.
- Writes mirror the same contiguous/cross-folio handling as reads.
- The helper assumes the extent buffer folio array represents a linear metadata address space.

Risk notes: This is foundational metadata access code. Incorrect offsets, field sizes, folio indexing, or missing bounds checks can corrupt on-disk metadata; the generated typed accessors in `accessors.h` are the main guardrail.
