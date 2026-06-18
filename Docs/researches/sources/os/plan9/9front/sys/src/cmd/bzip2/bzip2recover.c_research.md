# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2recover.c

This is upstream `bzip2recover`, a damaged `.bz2` block salvage tool.

Major responsibilities:
- Scans the input bitstream for bzip2 block header and end-marker magic values.
- Records candidate block bit ranges.
- Re-reads the input and writes each recoverable block as a standalone `.bz2` file named `recNNNN<original>`.
- Writes synthetic stream headers and end markers around recovered block data.

Notable implementation details:
- Uses stdio rather than Plan 9 `Biobuf`.
- Implements its own bit-level read/write abstraction `BitStream`.
- Fixed arrays hold up to 20,000 block ranges.
- Always writes recovered streams with block size marker `9`.

Risks and caveats:
- Source comments call it a complete hack.
- Fixed filename buffers are 2000 bytes.
- It can produce incomplete recovered blocks when EOF interrupts a candidate range.
