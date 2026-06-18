# sources/user-network-fs/samba/source3/rpc_server/dfs/srv_dfs_nt.c

Purpose: source3 implementation of the DFS RPC pipe, including add/remove/enumerate/get-info operations for MSDFS links stored through Samba shares and VFS DFS path hooks.

Important APIs/types/functions: `create_junction`, `junction_to_local_path_tos`, `create_msdfs_link`, `remove_msdfs_link`, `count_dfs_links`, `form_junctions`, `enum_msdfs_links`, `_dfs_Add`, `_dfs_Remove`, `_dfs_Enum`, and `_dfs_GetInfo`. Reply helpers populate `dfs_Info1`, `dfs_Info2`, `dfs_Info3`, and `dfs_Info100`.

Control flow: mutation calls require the caller's Unix UID to match `sec_initial_uid`. `_dfs_Add` parses the DFS path, resolves any existing referral via `get_referred_path`, appends a referral built from server/share input, then creates or replaces the DFS link through `SMB_VFS_CREATE_DFS_PATHAT`. `_dfs_Remove` resolves the path, either deletes the link entirely or clears a matching referral and rewrites the DFS path. Enumeration loads registry and usershare shares, counts DFS roots and links, creates synthetic root referrals, and enumerates link referrals under each DFS root.

State/persistence behavior: DFS state is persisted as filesystem DFS link objects under MSDFS root shares, not in process memory. Enumeration also depends on current share definitions, usershare registry loading, and optional `msdfs proxy` configuration.

Dependencies/integration: integrates loadparm share configuration, global messaging, fake connection creation, smbd VFS directory APIs, `msdfs.h` referral parsing, auth session information, and generated DFS RPC boilerplate.

Risks/test signals: path parsing deliberately rejects non-DFS roots and invalid non-POSIX syntax. Create uses unlink-and-retry on name collision, so tests should cover replacement and read-only shares. Enumeration count overflow handling, proxy roots, hidden path forms with leading separators, and unsupported DFS calls that set `DCERPC_FAULT_OP_RNG_ERROR` are important compatibility signals.
