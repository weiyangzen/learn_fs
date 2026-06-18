# File Research: sources/os/plan9/plan9/sys/src/9/pc/sd53c8xx.c

Plan 9 SCSI disk interface driver for NCR/Symbios/LSI Logic 53c8xx PCI SCSI controllers.

Key elements:
- Supports 53c810/815/825/860/875/885/895/896/1010/1011 variants through `variant[]`, with feature flags for wide, ultra, ultra2, prefetch, local RAM, big FIFO, differential, and clock multipliers.
- Defines memory-mapped NCR register layout `Ncr`, DMA move descriptors `Movedata`, request descriptor `Dsa`, controller state `Controller`, negotiation states, and transfer states.
- Includes generated SCRIPT microcode from `sd53c8xx.i`; `na_fixup` patches script-relative, register-relative, and external references.
- DSA management uses a controller-visible linked list with a sentinel `dsaend` to avoid controller walks through address zero.
- `synctabinit`, `chooserate`, `setsync`, `setasync`, `setwide`, `buildsdtrmsg`, `buildwdtrmsg`, and `msgsm` implement synchronous and wide SCSI negotiation.
- `softreset`, `busreset`, and `reset` initialize controller and SCSI bus state.
- `calcblockdma`, `read_mismatch_recover`, `write_mismatch_recover`, and `advancedata` handle DMA segmentation and phase-mismatch recovery.
- `sd53c8xxinterrupt` handles script interrupts, SCSI/DMA interrupts, phase mismatches, timeouts, parity/unexpected disconnects, script diagnostics, wakeups, and script restart/continue decisions.
- `sd53c8xxrio` is the main SCSI request path: allocates DSA, serializes per target, builds identify/negotiation/command/data/status descriptors, starts or signals SCRIPT execution, waits, handles timeout/reset, computes residual length, records target capabilities from INQUIRY, and issues REQUEST SENSE on check condition.
- `sd53c8xxpnp` discovers matching PCI devices, maps registers and optional local RAM, allocates/fixes SCRIPT memory, creates `SDev` instances, and links them.
- `sd53c8xxenable` enables bus mastering, initializes sync tables, captures BIOS settings, resets bus, and installs interrupt handler.
- Exports `SDifc sd53c8xxifc` with Plan 9 storage hooks: pnp, enable, verify, online, rio, bio.

Interactions:
- Heavy dependency on PCI enumeration/config and `vmap`.
- Implements a block-storage path through Plan 9 `sd` SCSI layer.
- Uses DMA address macros and controller-visible physical addressing assumptions for 386.
- Interrupt routing depends on PCI interrupt line/APIC/PIC setup.

Research notes:
- This is the most filesystem-relevant file in the group because it provides disk I/O substrate for SCSI storage.
- Known-problem comment notes read/write mismatch recovery may fail on 53c1010s.
- Driver is tightly coupled to generated NCR SCRIPT code and hardware phase behavior.
