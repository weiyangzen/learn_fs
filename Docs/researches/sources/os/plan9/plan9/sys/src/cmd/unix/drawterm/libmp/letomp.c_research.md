# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/letomp.c

Converts little-endian byte arrays to `mpint`.

Key function:
- `letomp`: optionally allocates output, sizes it, packs bytes into low-to-high `mpdigit` limbs, and sets final `top`.

Important behavior:
- Unlike `betomp`, it preserves packing order directly from least significant byte first.
