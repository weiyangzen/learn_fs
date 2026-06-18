# File Research: sources/virtualization/open-iscsi/usr/session_mgmt.h

Purpose: Declares session login/logout management helpers used by open-iscsi admin and daemon code.

Key declarations:
- Portal login helpers: `iscsi_login_portal()`, `iscsi_login_portal_nowait()`, `iscsi_login_portals()`, and `iscsi_login_portals_safe()`.
- Portal logout helpers: `iscsi_logout_portal()` and `iscsi_logout_portals()`.
- Session existence helper: `iscsi_check_for_running_session()`.

Implementation notes:
- Uses forward declarations for `struct node_rec`, `struct list_head`, and `struct session_info`, keeping the header lightweight.
- Batch login/logout APIs take callback function pointers so callers can supply filtering or alternate per-record behavior.

Dependencies and interactions:
- Implemented by `session_mgmt.c`; callers must include concrete node/list/session definitions where they build records or callbacks.

Filesystem/storage relevance:
- Exposes the high-level API for creating or removing iSCSI storage sessions from lists of configured portals or active session records.
