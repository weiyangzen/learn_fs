# File Research: sources/virtualization/spdk/lib/iscsi/iscsi_subsystem.c

Full-file read: 1356 lines.

This file owns iSCSI subsystem lifecycle, global option defaults/validation, mempool allocation, poll-group thread setup, CHAP auth group storage, and JSON config emission.

Main responsibilities:
- Defines global startup options pointer `g_spdk_iscsi_opts`.
- Allocates PDU, immediate-data, data-out, session, and task mempools.
- Allocates and validates `spdk_iscsi_opts`, then copies values into `g_iscsi`.
- Maintains CHAP auth groups and secrets, including config-file parsing.
- Initializes per-core iSCSI poll-group threads and socket pollers.
- Coordinates shutdown: closes portals, drains connections, releases channels, unregisters the I/O device, destroys pools and global lists.
- Emits iSCSI options and auth groups as JSON and contributes to `spdk_iscsi_config_json`.

Important control flow:
- `spdk_iscsi_init` stores callback state, parses globals, creates poll groups on every SPDK core, then completes after all poll groups report back.
- `iscsi_poll_group_poll` polls socket groups and destructs connections in `ISCSI_CONN_STATE_EXITING`.
- `shutdown_iscsi_conns_done` walks all channels and tears down poll groups.
- `iscsi_initialize_global_params` consumes `g_spdk_iscsi_opts` or creates defaults, then frees the options object.
- `iscsi_chap_get_authinfo` locks `g_iscsi.mutex` while copying auth secret material.

Integration points:
- Uses SPDK mempool, thread, I/O channel, poller, socket, conf, SCSI, and JSON writer APIs.
- Calls into `conn.c` for connection pools/shutdown, `portal_grp.c` for listener shutdown, `tgt_node.c` for target cleanup, and `init_grp.c` for initiator group destruction.
- Auth data created here is consumed during CHAP login.

Risks and review notes:
- Mempool initialization failure paths do not always free earlier pools immediately; final cleanup may rely on later shutdown paths.
- `iscsi_auth_group_info_json` writes CHAP secrets back into JSON output, so callers must treat config dumps as sensitive.
- `iscsi_parse_auth_info` destroys all auth groups on parse error, which is correct for atomic config loading but important operationally.
- `iscsi_poll_group_destroy` calls `spdk_thread_exit(thread)`, so lifecycle assumptions around SPDK thread ownership are tight.

Testing focus:
- Invalid option bounds and CHAP combinations.
- Auth file parse success/failure and duplicate users.
- Init/fini callback ordering across multiple cores.
- Pool leak detection via `iscsi_check_pools`.
