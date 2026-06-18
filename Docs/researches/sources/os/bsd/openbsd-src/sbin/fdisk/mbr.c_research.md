# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.c

## Purpose
Implements MBR initialization, conversion, printing, recovery, reading, writing, and validation.

## Key Behavior
- `MBR_init()` clears GPT globals, initializes either an extended MBR shell or a primary MBR with default boot code, optional boot partition, and OpenBSD partition.
- OpenBSD partition placement starts after a configured/default boot partition, after first track aligned to a power-of-two block, or after the MBR.
- `dos_mbr_to_mbr()` decodes on-disk `struct dos_mbr` into internal `struct mbr` and `struct prt` entries, recording how many leading bytes were zero.
- `mbr_to_dos_mbr()` encodes internal state back to on-disk little-endian DOS MBR structures.
- `MBR_print()` prints geometry, offset, signature, and four partition entries.
- `MBR_recover_partition()` parses printed MBR partition lines back into partition entries.
- `MBR_read()` reads a sector and decodes it.
- `MBR_write()` writes the MBR and reloads in-kernel disklabel info with `DIOCRLDINFO`.
- `MBR_valid_prt()` accepts all-zero MBRs as editable and otherwise validates signature and plausible partition bounds.

## Notes
This file deliberately keeps MBR-specific logic small and delegates CHS/LBA partition details to `part.c` outside this group.
