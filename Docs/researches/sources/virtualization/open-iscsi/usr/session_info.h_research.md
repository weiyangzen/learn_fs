# File Research: sources/virtualization/open-iscsi/usr/session_info.h

Purpose: Declares data structures and print/list APIs for active iSCSI session reporting.

Key definitions:
- `struct session_timeout` stores abort, LUN reset, recovery, and target reset timeouts.
- `struct session_CHAP` stores outgoing and incoming CHAP username/password strings.
- `struct session_info` stores local iface/SID/request-timeout fields plus remote target name, TPGT, current portal, and persistent portal details.
- `session_match_info_fn_t` is the callback type for filtering `session_info` entries.
- `struct session_link_info` passes list, match callback, and callback data into sysfs session iteration.
- `SESSION_INFO_*` flags select interface, negotiated parameters, state, SCSI devices, host devices, timeouts, and auth output.

Declared APIs:
- `session_info_create_list()`
- `session_info_free_list()`
- `session_info_print()`
- `session_info_print_tree()`

Dependencies and interactions:
- Includes libopeniscsiusr session declarations, generic `sysfs.h`, iSCSI protocol/config size definitions, and project list types.

Filesystem/storage relevance:
- Provides the structured representation used to correlate iSCSI sessions with portals, interfaces, authentication, timeouts, and attached storage devices.
