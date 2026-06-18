# File Research: sources/os/plan9/9front/sys/src/9/pc/sdmylex.c

## Role

SD/SCSI host adapter driver for Mylex MultiMaster and compatible BusLogic BT-* controllers, including 24-bit mailbox mode and 32-bit extended mailbox mode. The 24-bit path also supports Adaptec AHA-154xx-style adapters.

## Main Interfaces

- Exports `SDifc sdmylexifc` named `mylex`.
- PnP path `mylexpnp()` scans PCI Mylex devices, EISA IDs, and ISA `scsi` config entries of type `aha1542`.
- Main I/O callback `mylexrio()` dispatches to `mylex24rio()` or `mylex32rio()`.

## Key Behavior

- Defines 24-bit and 32-bit mailbox formats plus corresponding CCB layouts.
- `mylexprobe()` resets the adapter, probes extended setup support, unlocks AHA BIOS mailbox protection when needed, reads adapter ID/DMA/IRQ, and determines narrow vs wide target count.
- `mylex24rio()` builds 24-bit CCBs, stages buffers above 24-bit DMA space through temporary memory, submits through outgoing mailboxes, and waits for interrupt completion.
- `mylex32rio()` builds extended 32-bit CCBs with target/LUN/tag fields and optional tagged queueing.
- Request-sense optimization caches a completed check-condition CCB so a subsequent REQUEST SENSE can return embedded sense data without another adapter command.
- Interrupt paths walk incoming mailboxes, clear mailbox codes, set CCB completion flags, and wake sleepers.

## Dependencies And Assumptions

- Depends on Plan 9 SD/SCSI infrastructure and low-level I/O port access.
- 24-bit mode requires controller and DMA memory below 16 MiB unless a staging buffer is used.
- CCB count is fixed at `NMbox-1`; a TODO notes dynamic allocation is not implemented.
- Wide support is attempted only in the 32-bit path.

## Research Notes

- This is a classic mailbox SCSI driver rather than an ATA/SATA driver.
- The code carefully preserves the synchronous SD request contract: callers do not regain buffers until DMA completion.
- Initialization includes many compatibility paths for old BIOS/ISA/EISA adapter behavior.
