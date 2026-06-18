# File Research: sources/os/bsd/netbsd-src/lib/libutil/disklabel_dkcksum.c

## Purpose
Computes the classic NetBSD disklabel XOR checksum.

## Key Details
- `disklabel_dkcksum(struct disklabel *lp)` XORs 16-bit words from the start of the label through `d_partitions[d_npartitions]`.
- Returns the computed `uint16_t` checksum.
- A valid label checksum should evaluate consistently with the disklabel format expectations.

## Dependencies and Role
- Used by `disklabel_scan.c`.
- Directly relevant to disklabel discovery and validation.
