# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_bmap.c

Source read: complete file, 100 lines.

Purpose: Logical-to-physical block mapping for cd9660 files.

Key interface:
- `cd9660_bmap(struct vop_bmap_args *ap)` maps a file logical offset to a device offset by adding the file's starting extent (`iso_start << im_bshift`) to the logical offset.

Implementation notes:
- Returns success immediately when no physical offset is requested.
- Asserts the logical offset is block-aligned to the mounted ISO block size.
- Computes `a_runp` as readahead bytes remaining in the file, capped at `MAXBSIZE` and rounded down to block size.
- Sets backward run (`a_runb`) to zero.

Integration:
- Used by read/strategy paths and by directory buffer helpers that need stable physical offsets.
- Depends on `iso_node` mount block-shift and extent metadata.

Risks and review notes:
- ISO files are contiguous extents in this model; sparse or multi-extent semantics must be handled elsewhere if supported.
