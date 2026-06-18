# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_sysfs.c

Reads firmware iSCSI boot data from sysfs, covering both standard iBFT and low-level-driver `iscsi_boot*` sysfs layouts.

Main behavior:
- Searches `/sys/firmware/ibft/` and `/sys/firmware/iscsi_boot*/`.
- Uses `nftw` to collect `target*` and `ethernet*` directories.
- For boot info, selects NIC and target entries with the firmware-selected boot flag.
- For target enumeration, associates each target with a NIC via `nic-assoc` and NIC `index`.
- Fills `boot_context` with initiator name/ISID, boot root, target name/address/port/LUN/CHAP secrets, NIC MAC/interface/IP/VLAN/mask/prefix/gateway/DNS/DHCP/origin, boot NIC, boot target, and offload scsi host name when applicable.

Interface resolution:
- For iBFT, it first follows sysfs `device/net` links to find the Linux netdev.
- If unavailable, it falls back to MAC address lookup.
- For non-iBFT LLD roots, it records the sysfs subsystem as `scsi_host_name`.

Error handling:
- Missing optional fields are tolerated.
- Partial invalid entries are skipped if some valid targets were already found.
- On total failure, returns `ISCSI_ERR_NO_OBJS_FOUND` or sysfs lookup errors.
