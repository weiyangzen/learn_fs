# File Research: sources/os/plan9/9front/sys/src/cmd/aux/unbflz.c

`unbflz` decompresses a simple `BLZ\n` format from a file or stdin to stdout. It reads total output length, then a block table whose entries are either literal lengths marked with high bit set or copy lengths followed by source offsets.

After validating that summed block lengths equal the output length, it reconstructs into memory, reading literal runs from the input stream and copying backreferences from prior output. Its `copy` function deliberately copies forward byte by byte for overlap semantics.

All integers are big-endian. The full output buffer and block table are allocated in memory.
