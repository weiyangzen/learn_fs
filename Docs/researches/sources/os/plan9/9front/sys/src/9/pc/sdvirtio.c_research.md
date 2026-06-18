# File Research: sources/os/plan9/9front/sys/src/9/pc/sdvirtio.c

## Role

SD driver for legacy PCI virtio block and virtio SCSI devices.

## Main Interfaces

- Exports `SDifc sdvirtioifc` named `virtio`.
- PnP path `viopnp()` scans vendor `0x1af4`, legacy device range `0x1000..0x103f`, revision `0`, and subsystem type block (`2`) or SCSI (`8`).
- Runtime callbacks include `vioenable`, `viodisable`, `vioverify`, `vioonline`, `viorio`, and `viobio`.

## Key Behavior

- Implements legacy virtqueue layout with descriptor, avail, and used rings allocated page-aligned by `mkvqueue()`.
- `viopnpdevs()` resets devices, reads features, sets acknowledge/driver status, discovers queues, and writes queue physical page numbers.
- `vioblkreq()` builds simple block request chains: request header, optional data buffer, and one-byte status.
- `vioscsireq()` builds virtio SCSI command descriptors, including target/LUN, CDB, optional data buffer, response, sense, and residual handling.
- `viointerrupt()` handles queue completions and falls back to polling completions in `vqio()` if interrupts are missed.
- Block flush commands are translated from SCSI SYNCHRONIZE CACHE opcodes to virtio block type `4`.

## Dependencies And Assumptions

- Depends on Plan 9 PCI and SD/SCSI interfaces.
- Implements the legacy I/O-port virtio interface, not modern PCI capabilities.
- Does not negotiate feature bits beyond reading device features.
- Uses simple direct descriptor chains; no indirect descriptors or multi-segment scatter/gather.

## Research Notes

- The opening comment says “ethernet,” but the file implements block/SCSI storage.
- The block path caps BIOS-style transfer chunks at 32 sectors.
- Stack-allocated request/response structures are safe only because submission waits synchronously for completion before returning.
