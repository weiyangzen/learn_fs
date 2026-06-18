# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_event.c

Implements Linux PCI uevent listening and parsing for SPDK.

Important behavior:
- On Linux, opens a nonblocking `NETLINK_KOBJECT_UEVENT` socket subscribed to all groups.
- Attempts to set a 1 MiB receive buffer with `SO_RCVBUFFORCE` or `SO_RCVBUF`.
- Parses UIO `add`/`remove` events by extracting the PCI BDF from `DEVPATH`.
- Parses VFIO add events from `ACTION=bind`, `DRIVER=vfio-pci`, and `PCI_SLOT_NAME`.
- Fills `struct spdk_pci_event` with `SPDK_UEVENT_ADD` or `SPDK_UEVENT_REMOVE` plus parsed PCI address.
- Non-Linux builds return `-ENOTSUP`.

Integration note: VFIO hotremove itself is handled through DPDK callbacks in `pci.c`; this file mainly supports device add/allow notification paths.
