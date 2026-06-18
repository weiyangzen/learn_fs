# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_reg.h

## Purpose
Defines PMCS PCI IDs, BAR/register-set layout, message-unit register offsets, doorbell bits, scratchpad state fields, GSM/top-level register offsets, reset bits, flash/register-dump addresses, PCI config offsets, PHY-layer registers, and register accessor prototypes.

## Main Interfaces
- PCI identity constants for vendor/device and PM8001 revisions.
- Message unit offsets and bit definitions for inbound/outbound doorbells, scratchpads, MPI initiation/freeze/unfreeze/termination, interrupt masking, AAP/IOP states, and soft-reset signatures.
- GSM register constants cover NMI enables, reset/control, parity/ECC indicators, flash regions, shared memory, I/O status table, and ring buffers.
- Top-level registers include event/error interrupt control, AXI translation, outbound doorbell auto-clear, and interrupt coalescing timer/control.
- Reset bit masks define inverted chip reset fields and soft-reset component groups.
- Accessor prototypes cover message unit, GSM, top unit, MPI/GST/IQC/OQC tables, IQ/OQ indices, and their corresponding writes.

## Dependencies And Relationships
Used by PMCS setup/reset/interrupt/MPI/register-dump code and by queue macros in `pmcs_iomb.h`.

## Research Notes
The comments document four 64 KiB PCIe memory regions and the shifted window used for broader chip register access, which is central to understanding PMCS register mapping.
