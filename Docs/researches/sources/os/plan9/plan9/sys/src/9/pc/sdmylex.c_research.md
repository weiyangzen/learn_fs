# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdmylex.c

Purpose: Plan 9 `SDifc` driver named `mylex` for Mylex MultiMaster/BusLogic BT-series SCSI host adapters, supporting both 24-bit and 32-bit mailbox/CCB modes. It also supports AHA-1542-like 24-bit mailbox behavior.

Main structures:
- `Ctlr`: adapter I/O port, SCSI ID, bus mode, IRQ, wide mode, PCI device, mailbox state, CCB free list, and cached check-condition CCBs.
- `Mbox24`/`Mbox32`: outgoing/incoming mailbox formats for 24-bit and 32-bit controllers.
- `Ccb24`/`Ccb32`: command control blocks for 24-bit and 32-bit commands, including CDB, sense storage, DMA address fields, status fields, rendezvous, and free-list link.

Key logic:
- `mylexpnp` probes PCI Mylex devices, EISA signatures, and ISA `scsi` config entries of type `aha1542`.
- `mylexprobe` resets the controller, detects 24-bit vs 32-bit mode using extended setup inquiry, unlocks some AHA BIOS-protected mailbox interfaces, reads adapter SCSI ID/DMA/IRQ, and creates an `SDev`.
- `mylex24enable` allocates 24-bit-addressable mailbox/CCB memory, seeds the CCB free list, and initializes the board mailbox interface.
- `mylex32enable` allocates 32-bit mailbox/CCB memory, sets sense pointers, optionally enables wide mode, and initializes extended mailboxes.
- `mylexrio` dispatches requests to `mylex24rio` or `mylex32rio`, rejecting the adapter target ID and unsupported narrow targets.
- `mylex24rio` builds a 24-bit CCB, stages data through low memory if the request buffer is above 24-bit addressability, posts an outgoing mailbox, waits for completion, handles residual length and check-condition sense caching.
- `mylex32rio` builds a 32-bit CCB, includes target/LUN/tag fields, posts a mailbox, waits for completion, handles residual length and sense caching.
- `mylex24interrupt` and `mylex32interrupt` clear adapter interrupts, scan incoming mailboxes, recover the CCB pointer, mark it done, and wake the sleeping request.

Dependencies and integration:
- Uses Plan 9 SD layer through `SDifc sdmylexifc`.
- Uses generic SCSI verification/online/bio helpers; this driver passes CDBs directly to the adapter rather than translating to ATA.
- Uses port I/O, PCI/EISA/ISA discovery helpers, DMA/physical address macros, and Plan 9 rendezvous wait/wakeup.

Risks and notes:
- 24-bit mode requires bounce buffering for high physical addresses; allocation failure returns `SDmalloc`.
- Number of CCBs is fixed at `NMbox-1`; TODO notes mention dynamic allocation was not implemented.
- No disable/clear hooks are provided in the `SDifc`, so teardown is minimal compared with newer drivers.
- Several initialization waits are busy loops with no timeout beyond prior reset polling.
