# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap.c

## Purpose
Scrubs realtime bitmap metadata for a realtime group. It validates realtime geometry, metadata inode shape, bitmap file extents, free-space records, and cross-references free/used realtime extents against rtrmapbt and rtrefcountbt.

## Major Components
- `xchk_setup_rtbitmap`: allocates `xchk_rtbitmap`, initializes rtgroup and repair setup, allocates transaction, installs live bitmap inode, attaches dquots, locks rtgroup metadata, and computes geometry.
- `xchk_rtbitmap_xref`: cross-references free bitmap extents.
- `xchk_rtbitmap_rec`: validates each free extent record from bitmap query.
- `xchk_rtbitmap_check_extents`: ensures bitmap file has written mappings through EOF.
- `xchk_rtbitmap`: top-level scrub.
- `xchk_xref_is_used_rt_space`: public xref helper to assert realtime blocks are not free.

## Control Flow and Invariants
The scrubber checks:
- `sb_rextents`, `sb_rextslog`, and `sb_rbmblocks` match computed values.
- bitmap file size is fsblock-aligned and large enough.
- metadata inode forks are healthy.
- all bitmap file mappings are written.
- all free extent records are valid realtime block extents.
- free extents have no rtrmap owner, are not shared, and are not CoW staging.
- used ranges between free extents have rtrmap owners.

For zoned filesystems, `xchk_xref_is_used_rt_space` validates zone rgbno rather than querying rtbitmap free state.

## Dependencies and Integration
Uses rtgroup locking, realtime allocation query APIs, metadata inode scrub, rtrmap xref helpers, rtrefcount xref helpers, and repair setup from `rtbitmap_repair.c`.

## Risk and Edge Cases
- Geometry validation can flag the bitmap inode corrupt rather than continuing.
- The final used-range check uses rtgroup extent boundaries and can detect missing rtrmap ownership after the last free record.
- The scrubber tolerates growfsrt ordering by allowing bitmap files larger than current `sb_rbmblocks`.
