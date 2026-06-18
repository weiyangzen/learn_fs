# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwc.c

Shared LZW stream support code.

Key behavior:
- Defines the public GC structure for `stream_LZW_state`.
- `s_LZW_set_defaults` applies default decode parameters and clears the table pointer.
- `s_LZW_release` frees the allocated LZW table storage through `table.decode`, shared with the union used by encode/decode state.

Notable dependencies:
- LZW state definitions from `slzwx.h`.
- Ghostscript stream implementation macros.

Research notes:
- The release routine depends on encode and decode table pointers sharing the same union slot.
