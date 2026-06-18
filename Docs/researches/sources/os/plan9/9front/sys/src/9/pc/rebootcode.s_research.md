# File Research: sources/os/plan9/9front/sys/src/9/pc/rebootcode.s

Small x86 assembly routine used during reboot/kernel replacement.

Behavior:
- Entry `main(SB)` receives destination, source, and byte count.
- Disables paging by clearing CR0 PG bit and clears CR3.
- Sets stack pointer below the entry point.
- If destination/entry is zero, parks the CPU in an infinite `HLT` loop.
- Copies the new kernel image from source to destination, choosing forward or backward copy depending on overlap.
- Jumps directly to the physical entry point after the copy.
- Comment notes that the true virtual entry is `KZERO|AX`, but this code jumps before the new kernel enables its MMU.

Research notes:
- This code is deliberately physical-address oriented because paging is disabled before the copy.
- Its overlap logic is memmove-like: forward copy when safe, backward copy when source end overlaps destination.
- It is platform boot/reboot infrastructure, not a storage/filesystem component.
