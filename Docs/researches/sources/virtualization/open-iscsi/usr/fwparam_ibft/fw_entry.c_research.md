# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fw_entry.c

Provides the public firmware boot context entry points. It bridges PPC OpenFirmware and sysfs/iBFT readers, configures boot NICs, and prints firmware-derived idbm-style records.

Key functions:
- `fw_setup_nics` gets firmware targets, then configures software NICs with IPv4/IPv6 helpers or offload NICs via iface boot-context setup.
- `fw_get_entry` tries PPC boot info first, then sysfs boot info.
- `fw_get_targets` tries PPC target enumeration first, then sysfs target enumeration.
- `fw_free_targets` frees `boot_context` list entries.
- `fw_print_entry` emits initiator, network, and target fields between idbm record markers.

Dumped fields include initiator name/ISID/transport, MAC, boot protocol, IP/prefix/mask/gateway/DNS/VLAN/netdev, target name/address/port, CHAP credentials, and boot LUN.
