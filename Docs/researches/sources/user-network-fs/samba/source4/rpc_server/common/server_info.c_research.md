# sources/user-network-fs/samba/source4/rpc_server/common/server_info.c

Purpose: provides shared SRVSVC/server metadata helpers and central SAM database connection helpers for RPC server implementations.

Important APIs and control flow: server metadata helpers return platform id, server name normalization, server type flags, LAN root, user limits, announcement timers, license count, user path, and share-name validation. `dcesrv_common_get_server_type()` derives announce flags from `server_role`, optionally opens samdb as anonymous on AD DCs to decide PDC vs backup DC, and adds time-source/DFS flags from loadparm. `dcesrv_samdb_connect_session_info()` copies auth session info and remote address, opens samdb with those copies, and optionally stores audit session info in the LDB opaque `DSDB_NETWORK_SESSION_INFO`. `dcesrv_samdb_connect_as_system()` uses system credentials for writes needing elevated server authority while preserving caller audit details. `dcesrv_samdb_connect_as_user()` opens with the remote caller session.

State and persistence: metadata functions are mostly read-only with hardcoded compatibility values. SAM connection helpers do not write records but create live LDB contexts whose opaque audit state affects later audit logging.

Dependencies and integration: used by DNS, DRSUAPI, and other RPC servers. Depends on loadparm, SAMDB, auth/session utilities, roles, and tsocket address copying.

Risks and test signals: many SRVSVC values are hardcoded. Connection helper lifetimes are security-sensitive because copied session info must outlive the samdb context. Tests should cover anonymous/member/DC roles, PDC flag detection, invalid share-name characters, system vs user samdb access, and audit opaque propagation.
