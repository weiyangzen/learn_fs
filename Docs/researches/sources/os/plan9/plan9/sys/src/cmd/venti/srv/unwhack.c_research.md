# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unwhack.c

Purpose: Decompresses data encoded by the custom Venti `whack` compressor.

Key behavior:
- Maintains a bit buffer and decodes either literals or length/offset backreferences.
- Uses compact literal encoding influenced by recent literal history.
- Handles short and large match lengths, decodes offset classes, and copies from already produced output.
- Reports bounded errors through `Unwhack.err`.

Dependencies:
- Uses tables shared conceptually with `whack.c` and definitions from `whack.h`.

Notable details:
- Checks for too much output, offset before beginning of output, length overflow, and compressed data overrun.
