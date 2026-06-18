# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srld.c

RunLengthDecode stream filter.

Key behavior:
- Initializes defaults and dynamic copy state from `srlx.h` inline macros.
- `s_RLD_process` decodes PackBits/PostScript-style run-length records:
  - control byte `<128`: copy the next `b+1` literal bytes;
  - control byte `128`: EOD if `EndOfData` is true;
  - control byte `>128`: repeat next byte `257-b` times.
- Preserves partial literal or repeat runs across output-buffer exhaustion.

Notable dependencies:
- Shared run-length state from `srlx.h`.

Research notes:
- Literal-copy suspension uses `copy_data = -1`; repeat suspension stores the repeated byte in `copy_data`.
- If `EndOfData` is false, byte 128 is ignored rather than ending the stream.
