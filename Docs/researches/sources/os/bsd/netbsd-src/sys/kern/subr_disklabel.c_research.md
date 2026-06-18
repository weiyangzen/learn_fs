# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disklabel.c

## Summary
Provides a generic `setdisklabel()` implementation for ports without their own implementation or for rump kernels.

## Main Responsibilities
- Validates sector size, sectors per cylinder, disklabel magic, partition count, and checksum.
- Allows invalidation with magic `0xffffffff`.
- Prevents unsafe changes to open partitions.
- Preserves internally set partition information when a new label marks an open partition as unused.
- Recomputes and installs the label checksum before replacing the old label.

## Important Behavior
For every open partition, the new label must still contain that partition, must not change its offset, and must not shrink its size. This guards mounted/open users from having their backing range moved out from under them.

## Dependencies
Uses disklabel structures, `dkcksum()`, partition open masks, and optional DEBUG diagnostics.

## Risks
The function mutates `nlp` while preserving open partition metadata and recomputing checksum, so callers should not expect the input label object to remain byte-for-byte unchanged.
