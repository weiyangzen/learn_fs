# File Research: sources/virtualization/open-iscsi/usr/Makefile

Builds the user-space open-iscsi programs `iscsid`, `iscsiadm`, and `iscsistart`. It selects Linux netlink vs FreeBSD ioctl IPC objects, adds libkmod/libsystemd flags, enables iSNS support, and links against OpenSSL crypto, realtime, mount, iSNS, and `libopeniscsiusr`.

Important build groupings:
- Shared iSCSI library objects include auth, login, idbm, iface, transport, offload helpers, flashnode, and netlink code.
- Initiator runtime objects include `initiator.o`, `scsi.o`, `actor.o`, `event_poll.o`, `mgmt_ipc.o`, and kernel error tables.
- Discovery objects are `local_strings.o` and `discovery.o`.
- Firmware boot objects are delegated to `fwparam_ibft`.

Notable details:
- `KSUBLEVEL` is parsed from the kernel source Makefile to choose legacy `NETLINK_ISCSI` values.
- `DBROOT` and `HOMEDIR` compile into `ISCSI_DB_ROOT` and `ISCSI_CONFIG_ROOT`.
- `NO_SYSTEMD` disables libsystemd linkage and defines `NO_SYSTEMD`.
- `clean` removes local objects and recursively cleans `fwparam_ibft`, but does not clean `sysdeps`.
