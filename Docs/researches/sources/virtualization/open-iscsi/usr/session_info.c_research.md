# File Research: sources/virtualization/open-iscsi/usr/session_info.c

Purpose: Builds and prints active iSCSI session information for admin tooling, combining libopeniscsiusr session objects, sysfs attributes, daemon IPC state, interface records, negotiated parameters, timeouts, CHAP settings, and attached SCSI devices.

Key entry points:
- `session_info_create_list()` copies a `session_info` object into a sorted/grouped linked list, optionally filtered by a match callback.
- `session_info_free_list()` frees a list built by `session_info_create_list()`.
- `session_info_print()` prints session arrays at info levels 0 through 3.
- `session_info_print_tree()` prints grouped target/portal/session details according to bit flags.

Implementation notes:
- Flat output (`session_info_print_flat()`) prints transport, SID, persistent portal, TPGT, target name, and node type (`flash` or `non-flash`).
- Node type is inferred through `iscsi_sysfs_session_user_created()`: sessions without a user-created pid are treated as flash.
- `print_iscsi_state()` sends `MGMT_IPC_SESSION_INFO` to `iscsid` for daemon connection/internal state and reads kernel session state from sysfs.
- `print_iscsi_params()` reads negotiated session and connection config from sysfs and prints valid operational values only.
- `print_scsi_state()` maps SID to host number, optionally prints host state, and iterates attached devices.
- `print_scsi_device_info()` prints each host/target/lun, block-device name, and device state when available.
- Tree output groups consecutive sessions by target name and current portal, prints current and persistent portals, then conditionally prints interface, state, timeouts, CHAP, negotiated parameters, and SCSI devices.
- Passwords are masked unless `do_show` is set.
- Info level behavior: level 0/default prints flat lines; level 1 includes state and iface; level 2 adds iSCSI params, timeouts, and auth; level 3 adds kernel/tool version and SCSI/host devices.

Dependencies and interactions:
- Uses `libopeniscsiusr` getters for session fields.
- Uses open-iscsi sysfs helpers for transport, state, negotiated params, host numbers, LUN iteration, device state, and kernel version.
- Uses management IPC through `iscsid_exec_req()` and `MGMT_IPC_SESSION_INFO`.
- Uses `iface_print()` for interface details.

Filesystem/storage relevance:
- This is the user-visible inspection layer for active iSCSI-backed storage sessions, including portal identity, negotiated block-transfer parameters, authentication settings, and attached SCSI/block devices.
