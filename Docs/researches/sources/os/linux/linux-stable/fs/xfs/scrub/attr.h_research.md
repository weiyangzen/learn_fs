# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr.h

## Purpose
Declares temporary extended attribute scrub/repair buffer state and shared helper prototypes.

## Key Structures
`struct xchk_xattr_buf` stores:
- `usedmap`: byte bitmap for occupied space in shortform/leaf xattr storage.
- `freemap`: byte bitmap for advertised free space in leaf blocks.
- `name`: salvage/reinsert name scratch buffer.
- `value` and `value_sz`: scratch buffer for attr value extraction and reinsertion.

## API
- `xchk_xattr_set_map`
- `xchk_setup_xattr_buf`

## Notes
This header is shared by attr scrub and repair so both can reuse the same scratch allocation and byte-range validation helpers.
