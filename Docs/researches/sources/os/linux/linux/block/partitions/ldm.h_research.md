# File Research: sources/os/linux/linux/block/partitions/ldm.h

## Summary
Defines constants and in-memory structures for Windows LDM dynamic disk parsing.

## Main Contents
- Magic values for `VMDB`, `VBLK`, `PRIVHEAD`, and `TOCBLOCK`.
- VBLK type and flag constants.
- LDM database sector offsets and database size constants.
- On-parser structures for fragments, private headers, TOCs, VMDB headers, VBLK variants, generic VBLKs, and the cached `ldmdb`.

## Important Details
All offsets and sizes in `privhead` and LDM database constants are sector-based. `struct vblk` stores common VBLK identity fields and a union of parsed record-specific payloads, then links into one of several per-type lists.

## Risks
Many constants encode fixed offsets into undocumented Windows structures. Parser code must keep these structures synchronized with the offset logic in `ldm.c`.
