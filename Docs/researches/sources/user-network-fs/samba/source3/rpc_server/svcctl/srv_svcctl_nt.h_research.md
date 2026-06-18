# sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_nt.h

Purpose: Header exposing SVCCTL service operation table lifecycle functions.

Important APIs: `init_service_op_table()` initializes the global service-name-to-operations table; `shutdown_service_op_table()` frees it. These are used by SVCCTL endpoint init/shutdown wrappers.

Control flow and state: No state in the header; the implementation owns `svcctl_ops`. Successful initialization is prerequisite for service lookup and handle creation.

Dependencies and integration: Used by SVCCTL RPC server setup. It has minimal declarations and relies on surrounding Samba includes for boolean type definitions.

Risks and test signals: If initialization is skipped or fails, service opens can dereference missing operation tables. Compile coverage plus SVCCTL endpoint startup/shutdown tests are appropriate.
