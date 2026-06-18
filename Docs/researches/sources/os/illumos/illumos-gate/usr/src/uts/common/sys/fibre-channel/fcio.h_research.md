# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fcio.h

Defines the user/kernel FCIO ioctl ABI for Fibre Channel port management. It assigns `FCIO_CMD`, subcommands for device enumeration, symbolic names, login/logout, topology, reset, diagnostics, name service, firmware/FCODE download, node-id operations, and T11 FC-HBA/NPIV library operations.

Key contracts are `fc_port_dev_t`/`fc_ns_map_entry_t`, `fcio_t`, and T11 HBA exchange structures such as `fc_hba_list_t`, `fc_hba_single_t`, `fc_hba_adapter_attributes_t`, `fc_hba_port_attributes_t`, and `fc_hba_adapter_port_stats_t`. The file also provides 32-bit syscall variants where pointer and size layout differs.

Dependencies are `fc_types.h` and `fc_appif.h` for WWNs, port IDs, HBA state-change types, and topology/state definitions. Treat this file as stable ABI: structure sizes, version fields, flexible one-element arrays, and `_SYSCALL32` packing are externally visible.
