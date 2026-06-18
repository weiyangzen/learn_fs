# File Research: sources/os/plan9/plan9/sys/src/9/pc/rebootcode.s

MMU-off kernel relocation and jump code used during reboot/loading a new kernel image.

Key elements:
- Entry `main` receives destination, source, and byte count.
- Disables paging by clearing CR0 PG and zeroing CR3.
- Copies source to destination with overlap handling: forward if safe, backward if overlapping.
- Jumps to the physical entry point after relocation.
- Notes that virtual `KZERO|AX` entry cannot be used until new kernel assembly re-enables MMU.

Interactions:
- Used by reboot/new-kernel handoff logic elsewhere.
- Depends on `mem.h` constants.

Research notes:
- Minimal assembly relocation stub; important for kernel lifecycle, not filesystem logic.
