# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/realmode.c

This file wraps the assembly real-mode transition used to invoke BIOS interrupts from the protected-mode bootstrap kernel.

Key responsibilities:
- Serializes BIOS calls with `rmlock`.
- Copies the requested `Ureg` to low memory at `RMUADDR`.
- Patches the interrupt number into `realmodeintrinst`.
- If not PXE-loaded at the expected low address, copies the real-mode assembly code to `RMCODE`.
- Temporarily identity maps low memory, switches CR3 to the bootstrap page directory, disables hardware interrupts, calls `realmode0`, then restores paging and interrupt state.
- Copies the resulting registers back to the caller’s `Ureg`.

Filesystem/storage relevance:
- Critical for BIOS INT 13 disk I/O used by early boot storage paths.
- Must be used carefully because it disables normal interrupt handling and temporarily changes low-memory mappings.
