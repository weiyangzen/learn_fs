# File Research: sources/os/plan9/9front/sys/src/9/pc/apbootstrap.s

x86 application-processor bootstrap trampoline for the PC port.

Key behavior:
- Starts in real mode from low conventional memory and far-jumps into `_apbootstrap`.
- Loads a small GDT, enables protected mode, sets segment registers, and far-jumps to 32-bit code.
- `_ap32` temporarily double-maps `KZERO` at virtual zero through the supplied page directory, enables PSE paging, and jumps into high virtual execution.
- `_appg` removes the temporary low mapping, sets an AP stack, clears flags, and calls the AP startup vector with APIC information.
- Defines embedded data slots `_apvector`, `_appdb`, and `_apapic`, plus the minimal GDT and descriptor pointer.

Research notes:
- Must be placed on a 4 KB boundary in the first MB, with comments noting an effective first-64 KB restriction.
- This is bootstrap code for SMP AP startup, not storage/filesystem logic.
