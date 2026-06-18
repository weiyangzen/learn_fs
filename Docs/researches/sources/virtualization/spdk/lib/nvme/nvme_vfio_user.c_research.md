# File Research: sources/virtualization/spdk/lib/nvme/nvme_vfio_user.c

## Purpose
Implements SPDK NVMe transport operations for `SPDK_NVME_TRANSPORT_VFIOUSER`, adapting the existing PCIe NVMe controller/qpair machinery to a vfio-user PCI endpoint.

## Main Responsibilities
- Defines `struct nvme_vfio_ctrlr`, embedding `struct nvme_pcie_ctrlr` and adding vfio-user device state plus a mapped doorbell base.
- Implements NVMe register accessors through `spdk_vfio_user_pci_bar_access()` against BAR0 or PCI config space.
- Maps BAR0 doorbells with `spdk_vfio_user_get_bar_addr()`.
- Constructs a controller from `trid->traddr/cntrl`, sets up vfio-user, initializes PCI command bits for bus mastering and INTx disable, reads CAP, builds admin qpair, and registers process state.
- Enables the controller by programming ASQ, ACQ, and AQA through vfio-user register writes.
- Destructs by destroying admin qpair, finishing generic controller teardown, releasing vfio-user device, and freeing the wrapper.

## Key Interfaces
- Exports `vfio_ops` as `const struct spdk_nvme_transport_ops`.
- Reuses PCIe qpair operations for I/O queues, polling, request submission, completion, and admin AER abort.
- Registers itself with `SPDK_NVME_TRANSPORT_REGISTER(vfio, &vfio_ops)`.

## Important Details
- Transfer constraints are hardcoded as `NVME_MAX_XFER_SIZE = 131072` and `NVME_MAX_SGES = 1`.
- Admin queue size is clamped to at least `NVME_PCIE_MIN_ADMIN_QUEUE_SIZE`.
- Doorbell stride is derived from CAP.DSTRD as `1 << cap.bits.dstrd`, matching PCIe controller expectations in units of 32-bit doorbells.
- `ctrlr_scan` only accepts `SPDK_NVME_TRANSPORT_VFIOUSER` and validates the target address exists before probing.

## Storage Relevance
This file is the host-side bridge that lets SPDK’s NVMe stack operate against a virtualized vfio-user NVMe PCI device while preserving the normal NVMe PCIe queue and completion model.

## Risks / Notes
- BAR/register access errors generally abort setup or return `-EIO` from enable paths.
- The code assumes the vfio-user endpoint exposes a controller path under `<traddr>/cntrl`.
- This transport disables CMB SQ use, so queue memory stays in host-managed memory.
