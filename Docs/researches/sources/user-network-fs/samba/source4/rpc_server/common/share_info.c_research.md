# sources/user-network-fs/samba/source4/rpc_server/common/share_info.c

Purpose: supplies common share metadata helpers for RPC share enumeration and query paths.

Important APIs and control flow: `dcesrv_common_get_share_permissions()`, `get_share_current_users()`, `get_share_dfs_flags()`, and `get_security_descriptor()` currently return hardcoded placeholder values. `dcesrv_common_get_share_type()` combines browseability with `SHARE_TYPE` to return disk, printer, IPC, and hidden flags. `dcesrv_common_get_share_path()` returns an empty path for IPC shares; otherwise it reads the share path, converts `/` to `\`, and prefixes it with `C:`.

State and persistence: read-only over `share_config`; no database writes. Returned strings are talloc-managed. Several comments state values should eventually come from an LDB database.

Dependencies and integration: depends on `param/share.h`, generated SRVSVC constants, and common share headers. These helpers feed SRVSVC-style RPC outputs.

Risks and test signals: path mapping is Windows-compatible but simplistic and assumes a `C:` drive prefix. Security descriptors are not exposed. Tests should cover IPC, printer, hidden/non-browseable, empty path, slash conversion, and NULL path allocation behavior.
