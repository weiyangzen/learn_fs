# File Research: sources/os/plan9/plan9/sys/src/9/ip/ptclbsum.c

Implements the low-level 16-bit checksum accumulator used by protocol checksum code.

Key behavior:
- `ptclbsum` computes a partial Internet checksum over a contiguous byte range.
- Handles odd starting alignment, trailing odd byte, little- vs big-endian host layout, chunked 16-byte accumulation, and final carry folding.
- Returns the unfolded checksum sum; callers such as `ptclcsum` complement it for final protocol checksums.

Notable design:
- Uses a static runtime endian probe through a short value and byte pointer.
