# sources/user-network-fs/samba/source4/ntvfs/ntvfs_base.c

Purpose: supplies the global NTVFS backend registry, ABI compatibility checks, connection stack construction, default IPC$ share injection, and module initialization.

Important APIs and functions: `ntvfs_register` validates `struct ntvfs_critical_sizes`, rejects duplicate name/type pairs, deep-copies `ntvfs_ops`, and appends to the static backend array. `ntvfs_backend_byname` resolves a registered backend by name and `enum ntvfs_type`. `ntvfs_interface_version` and `ntvfs_interface_differs` implement ABI checks. `ntvfs_init_connection` creates `struct ntvfs_context` and a linked stack of `ntvfs_module_context` objects from the share `ntvfs handler` list. `ntvfs_init` loads static/shared modules and ensures IPC$ exists.

Control flow: process startup calls `ntvfs_init`, which is guarded by a static `initialized` flag, loads modules, and calls `ntvfs_add_ipc_share`. Tree-connect setup calls `ntvfs_init_connection`, which reads handler names from share config, resolves each backend for the requested type, assigns depth, and appends module contexts in order.

State and persistence: registered backends live in static process memory for the life of the server. `ntvfs_init_connection` allocates per-connection state under the caller's talloc context and steals the share config. IPC$ addition mutates the loadparm service table if no IPC$ service exists.

Dependencies and integration points: depends on `share_string_list_option`, loadparm service APIs, Samba module loading, and dlink list helpers. Backend modules register through this file and later dispatch through `ntvfs_interface.c`.

Risks: static registry is not explicitly synchronized; duplicate backend names by type are rejected; missing handler config or missing registered backend returns internal error; ABI checks compare only selected critical sizes and version. Test signals include duplicate registration, unknown handler failure, multiple stacked handlers preserving order/depth, idempotent `ntvfs_init`, and automatic IPC$ creation with handler `default`.
