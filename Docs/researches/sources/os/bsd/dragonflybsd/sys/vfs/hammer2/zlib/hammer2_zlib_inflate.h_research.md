# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.h

Source read: complete file, 113 lines.

Purpose: Internal inflate state definition for the HAMMER2-local zlib copy. It declares the inflate mode enum and the full persistent `struct inflate_state` used across repeated `inflate()` calls.

Key definitions:
- `inflate_mode` enumerates header, dictionary, deflate block, code decode, trailer, terminal, and error states. Gzip-specific states are present even though the local inflate implementation primarily handles zlib/raw deflate.
- `struct inflate_state` stores wrapper flags, dictionary status, checksum, output totals, sliding-window metadata, input bit accumulator, copy/match fields, current decode-table pointers, dynamic Huffman table build workspace, and diagnostic fields such as `back` and `was`.
- `lens[320]`, `work[288]`, and `codes[ENOUGH]` provide fixed-size scratch and decode-table storage for dynamic blocks.

Integration:
- Requires `code` and `ENOUGH` from `hammer2_zlib_inftrees.h`.
- Read and written by `hammer2_zlib_inflate.c` and `hammer2_zlib_inffast.c`.

Risks and review notes:
- The state is large, roughly 10 KiB by the upstream comment, so allocation failures and kernel memory type consistency matter.
- The enum documents gzip transitions that are not fully implemented in this file set, so the structure can overstate supported stream formats.
