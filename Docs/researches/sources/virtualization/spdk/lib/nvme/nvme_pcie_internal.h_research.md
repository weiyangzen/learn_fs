# File Research: sources/virtualization/spdk/lib/nvme/nvme_pcie_internal.h

## Purpose

Private PCIe transport header defining controller/qpair/tracker layouts, queue constants, doorbell helpers, and function prototypes shared by `nvme_pcie.c` and `nvme_pcie_common.c`.

## Main Contents

- Queue sizing constants: min/max completion batch sizes, max SGL descriptors, max PRP list entries, minimum admin queue size.
- `struct nvme_pcie_ctrlr`: embeds generic controller plus MMIO register mapping, CMB state, PMR state, doorbell stride/base, PCI handle, and SIGBUS remap flag.
- `struct nvme_tracker`: one 4 KiB tracker per CID containing request pointer, callback, PRP/SGL bus address, metadata SGL, and union of PRP list or SGL descriptors. Static asserts enforce 4 KiB size and qword alignment.
- `struct nvme_pcie_poll_group`: generic transport poll group plus shared PCIe statistics.
- `struct nvme_pcie_qpair`: hot-path doorbells, SQ/CQ buffers, tracker queues, stats, indices, flags, embedded generic qpair, shadow doorbells, ownership state, bus addresses, and optional user-provided queue memory.
- Inline container conversions for generic-to-PCIe controller/qpair.
- Shadow doorbell event-index logic and SQ/CQ doorbell ringing helpers.
- Prototypes for controller, qpair, tracker, poll-group, and stats functions.

## Integration Points

This header is the contract between transport setup and qpair data path files. It also exposes `g_thread_mmio_ctrlr`, used by MMIO writes and the SIGBUS fault handler in `nvme_pcie.c`.

## Risk Notes

The header encodes layout-sensitive invariants. Changes to `struct nvme_tracker` can break the 4 KiB PRP boundary guarantee, while moving qpair fields can affect hot-path cache locality and doorbell correctness.
