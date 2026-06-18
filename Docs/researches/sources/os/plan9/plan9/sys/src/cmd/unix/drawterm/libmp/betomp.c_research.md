# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/betomp.c

Converts big-endian byte arrays to `mpint`.

Key function:
- `betomp`: optionally allocates output, skips leading zeros, sizes the target, and packs bytes into `mpdigit` limbs from most significant byte first.

Important behavior:
- Sets `top` based on requested bits before filling digits.
- Does not call `mpnorm`; leading zeros are stripped before packing.
