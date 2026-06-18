# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_disklabel.c

Local disklabel scan/checksum routines for `libukfs`.

Key responsibilities:
- Scans a memory buffer for a NetBSD disklabel by checking both magic fields.
- Supports byte-swapped labels.
- Validates:
  - partition count does not exceed `UKFS_MAXPARTITIONS`,
  - disklabel checksum is valid.
- Computes disklabel checksum by XORing 16-bit words through the partition array, optionally byte-swapping each word.

Important functions:
- `ukfs__disklabel_scan`
- `ukfs__disklabel_dkcksum`

Role in subsystem:
- Enables `%DISKLABEL:x%` partition probing in `ukfs.c` without depending on NetBSD-only `libutil`.
