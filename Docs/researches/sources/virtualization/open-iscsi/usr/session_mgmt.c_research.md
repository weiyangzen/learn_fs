# File Research: sources/virtualization/open-iscsi/usr/session_mgmt.c

Purpose: Implements admin-side helpers for requesting iSCSI session login/logout operations from `iscsid`, including batching, async request tracking, multi-session creation, and active-session checks.

Key entry points:
- `iscsi_login_portal()` logs into one portal record, honoring `session.nr_sessions` and `session.multiple`.
- `iscsi_login_portal_nowait()` sends login requests and closes async request fds without waiting for final results.
- `iscsi_login_portals()` logs into every record on a list and frees the list afterward.
- `iscsi_login_portals_safe()` performs the same batching without clearing the caller's list.
- `iscsi_logout_portal()` sends a logout request for a specific `session_info`.
- `iscsi_logout_portals()` discovers active sessions, applies a caller-provided logout filter/function, and optionally waits for all logouts.
- `iscsi_check_for_running_session()` checks sysfs for an existing session matching a node record.

Implementation notes:
- Async requests are tracked in `struct iscsid_async_req`, which stores a list node, caller data pointer, and socket fd.
- `__iscsi_login_portal()` sends either sync or async `MGMT_IPC_SESSION_LOGIN` requests by node record and logs immediate failures.
- `iscsi_login_portal()` counts existing matching sessions through `iscsi_sysfs_for_each_session()` and only creates missing sessions up to `rec->session.nr_sessions`.
- For multi-session records, it sets `rec->session.multiple` before issuing repeated login requests.
- `__iscsi_login_portals()` batches logins, waits with `iscsid_login_reqs_wait()` when requested, otherwise closes pending fds.
- Logout batching first builds a `session_info` list from sysfs, then applies the caller's logout function to each entry and waits/closes async requests according to the `wait` flag.
- Logging helpers report target, iface, portal, SID, and detailed iSCSI error text through `iscsi_err_print_msg()`.

Dependencies and interactions:
- Uses management IPC helpers from `iscsid_req.h` with `MGMT_IPC_SESSION_LOGIN` and `MGMT_IPC_SESSION_LOGOUT`.
- Uses sysfs session iteration and match callbacks from `iscsi_sysfs.h`.
- Uses `session_info_create_list()` and `session_info_free_list()` for logout target discovery.
- Uses IDBM node records and project list primitives.

Filesystem/storage relevance:
- This file is the admin orchestration layer that turns configured iSCSI node records into active kernel sessions and tears down active storage sessions selected from sysfs.
