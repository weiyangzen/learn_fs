# File Research: sources/virtualization/open-iscsi/usr/meson.build

Purpose: Defines Meson source groupings for the open-iscsi userspace programs under `usr`.

Key definitions:
- Enters `fwparam_ibft` with `subdir('fwparam_ibft')`.
- `iscsi_lib_srcs` is the common library-like source set shared by user tools. It includes login, sysfs, session info, transport, netlink IPC, iface, IDBM, flashnode, and utility code.
- `initiator_srcs` adds daemon initiator pieces such as `initiator.c`, `scsi.c`, event polling, management IPC, and kernel error tables.
- `discovery_srcs` contains discovery support.
- `iscsid_srcs`, `iscsiadm_srcs`, and `iscsistart_srcs` add program-specific main/control files.
- `iscsi_usr_arr` maps executable names (`iscsid`, `iscsiadm`, `iscsistart`) to the file arrays built from those source groups.

Implementation notes:
- `session_mgmt.c` and `mntcheck.c` are compiled into both `iscsid` and `iscsiadm`.
- `mgmt_ipc.c` is daemon-side and only part of the `iscsid` source set through `initiator_srcs`.
- `netlink.c`, `transport.c`, `uip_mgmt_ipc.c`, `session_info.c`, and `login.c` are common across the three programs through `iscsi_lib_srcs`.

Dependencies and interactions:
- This file does not declare link libraries or targets directly in the viewed content; it prepares source arrays consumed by surrounding Meson build files.

Filesystem/storage relevance:
- The build layout shows which storage-control features are shared by administration, daemon, and early-start tools, and which are daemon-only control-plane pieces.
