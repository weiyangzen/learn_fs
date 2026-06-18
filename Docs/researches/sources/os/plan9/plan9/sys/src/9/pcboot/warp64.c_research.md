# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/warp64.c

This file performs the final handoff from the 32-bit bootstrap to a 64-bit kernel entry point.

Key responsibilities:
- Uses CPUID extended function checks to detect long-mode support.
- `warp64` rejects 64-bit kernels on CPUs without long mode.
- Builds the Multiboot handoff block via `mkmultiboot`.
- Calls `impulse` before invoking the assembly `_warp64` entry trampoline.
- Converts the 64-bit kernel entry from high virtual address form by masking with the expected 64-bit `KZERO`.

Filesystem/storage relevance:
- Final boot handoff only. Storage relevance is indirect through preserving bootline and memory-map state for the loaded kernel.
