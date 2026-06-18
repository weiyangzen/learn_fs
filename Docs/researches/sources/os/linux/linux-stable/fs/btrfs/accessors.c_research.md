# File Research: sources/os/linux/linux-stable/fs/btrfs/accessors.c

## Summary
Implements generic little-endian get/set helpers for Btrfs extent-buffer metadata fields, including fields that span folio boundaries.

## Main Responsibilities
- Reads and writes 8/16/32/64-bit values from extent buffers.
- Handles metadata items split across two folios.
- Reports out-of-bounds member access.
- Implements `btrfs_node_key()` for reading node key pointers.

## Important Behavior
The generated helper macro computes a linear member offset, maps it to extent-buffer folio index and folio offset, validates bounds against `eb->len`, then either performs direct unaligned little-endian access or copies split bytes through a temporary buffer.

For setters, values are encoded into little-endian bytes and split back across folios when needed.

## Risks
These helpers are used throughout Btrfs metadata parsing and mutation. Incorrect split-folio handling or bounds checks would corrupt on-disk metadata or hide tree-checker problems.
