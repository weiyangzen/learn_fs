# File Research: sources/virtualization/spdk/lib/nvme/nvme_pcie.c

## Purpose

Implements the PCIe NVMe transport registration and controller-level PCIe behavior: device enumeration, hotplug/remove handling, MMIO register access, BAR/CMB/PMR mapping, controller construction/destruction, admin queue enablement, interrupt enablement, and transport operation table wiring.

## Main Responsibilities

- Register the SPDK PCI NVMe driver and `pcie_ops` transport.
- Handle PCI hotplug add/remove events and explicit physical removal checks.
- Protect MMIO access from SIGBUS on removed devices by tracking the current thread’s MMIO controller and remapping registers to an anonymous page on fault.
- Provide register accessor callbacks for 32-bit and 64-bit NVMe controller registers.
- Map/unmap BAR0, set doorbell base, discover/map CMB and PMR regions, and expose controller memory/persistent memory mapping APIs.
- Enumerate PCI devices, handle primary vs secondary process attach behavior, filter by requested PCI address, and call generic NVMe probe/construct logic.
- Construct PCIe controllers: claim PCI device, allocate `nvme_pcie_ctrlr`, set quirks/NUMA, construct generic controller, map BARs, enable busmaster/disable INTx, compute doorbell stride, construct admin qpair, and add process state.
- Destroy controllers and release admin qpair, generic controller state, BAR mappings, interrupts, PCI claim, and device attachment.

## Key Control Flow

`nvme_pcie_ctrlr_scan()` optionally parses `traddr`, processes hotplug removal events, and calls either full enumeration or direct attach. `pcie_nvme_enum_cb()` formats the PCI BDF into an NVMe transport ID and either attaches secondary processes to existing controllers or probes in the primary process.

`nvme_pcie_ctrlr_construct()` is the main setup path and culminates in `nvme_pcie_ctrlr_construct_admin_qpair()`. `nvme_pcie_ctrlr_enable()` writes ASQ, ACQ, and AQA based on the admin qpair buffers.

## Integration Points

Works with common qpair code in `nvme_pcie_common.c`, structures/inlines from `nvme_pcie_internal.h`, generic controller logic in `nvme_internal.h`, and environment PCI/MMIO/memory registration APIs.

## Risk Notes

- Several construction failure paths after BAR allocation/admin qpair setup rely on generic destructors only in some branches; lifetime ordering is subtle.
- SIGBUS handler uses global/thread-local controller state and remaps MMIO space, so correctness depends on every MMIO access setting/clearing `g_thread_mmio_ctrlr`.
- Secondary processes are explicitly rejected in interrupt mode.
