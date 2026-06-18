# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fdisk.h

## Scope

Complete file read, 173 lines. This header defines the x86/AT386 MBR/fdisk partition sector layout and partition type constants.

## Public Surface

It defines BIOS CHS bounds `MAX_SECT`, `MAX_CYL`, and `MAX_HEAD`; MBR constants `BOOTSZ`, `FD_NUMPART`, `MBB_MAGIC`, `DEFAULT_INTLV`, `MINPSIZE`, and `TSTPAT`.

It exports:

- `struct ipart`: one 16-byte fdisk partition entry with boot flag, CHS fields, system id, relative start sector, and sector count.
- Boot flags `NOTACTIVE` and `ACTIVE`.
- Many `systid` constants for DOS, Windows, Linux, Solaris, BSD, EFI, and other partition types.
- `MAXDOS`.
- `struct mboot`: master boot block with 440-byte boot code, Vista disk-id-compatible fields, four partition slots as bytes, and signature.
- On x86/amd64: `FDISK_PART_TABLE_START` and `MAX_EXT_PARTS`; otherwise `MAX_EXT_PARTS` is 0.

## Behavior And Integration

This header describes sector 0 layout for MBR-partitioned disks. Unix slices are not defined here; they are obtained from the VTOC inside the Solaris partition.

## Dependencies And Invariants

The `BOOTSZ` value of 440 intentionally preserves the Windows Vista disk ID area. `struct mboot.parts` is a byte array to avoid compiler alignment changes in the partition table.

## Risks

MBR layout is byte-exact. Any attempt to embed `struct ipart parts[4]` directly in `struct mboot` can break alignment. CHS constants contain historical fence values and must not be treated as modern capacity limits.
