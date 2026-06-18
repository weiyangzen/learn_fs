# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.h

Purpose: Public definitions for the `whack` compressor/decompressor.

Key behavior:
- Defines compressor stats count, error buffer length, max offset, hash table sizing, minimum match length, and decode constants.
- Defines `Whack` dictionary state and `Unwhack` error state.
- Declares `whackinit`, `unwhackinit`, `whack`, `unwhack`, and `whackblock`.

Dependencies:
- Used by `whack.c`, `unwhack.c`, and server code that selects compression.

Notable details:
- Compressor state contains a 16K hash table and 16K next-link table.
