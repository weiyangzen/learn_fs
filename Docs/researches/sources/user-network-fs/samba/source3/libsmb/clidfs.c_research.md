# sources/user-network-fs/samba/source3/libsmb/clidfs.c

## Purpose

`clidfs.c` implements client-side SMB connection management around DFS-aware path resolution. It is the layer that opens or reuses `cli_state` connections to `\\server\share`, negotiates protocol/session/tree state, follows DFS referrals, handles MSDFS proxy shares, and converts local paths to or from DFS-root full paths when the lower SMB1/SMB2 file APIs need a particular form.

## Important APIs, Types, and Functions

- `cli_cm_open()` is the public connection-manager entry point. It searches the linked list rooted at `referring_cli` for an existing connection to the requested server/share and opens a new connection only when needed.
- `do_connect()` performs the actual connect: `cli_connect_nb()`, SMB negotiate with SMB2 POSIX negotiate context, session setup, optional encryption enablement, optional MSDFS proxy detection, and tree connect.
- `cli_cm_connect()` wraps `do_connect()`, inserts new DFS child connections into the `cli_state` DLIST, and copies requested UNIX extension capabilities to referral targets.
- `cli_dfs_get_referral_ex()` and `cli_dfs_get_referral()` issue DFS referral requests using SMB2 `FSCTL_DFS_GET_REFERRALS` or SMB1 `TRANSACT2_GET_DFS_REFERRAL`, then parse referral version 3 entries into `struct client_dfs_referral`.
- `cli_resolve_path()` is the main DFS resolver. It probes whether a path is ordinary or covered by DFS, opens IPC$ to fetch referrals, reuses or opens target connections, splices unconsumed path components, and recursively follows nested referrals.
- `cli_check_msdfs_proxy()` detects shares that are actually proxy referrals by temporarily switching to IPC$, asking for a referral, and returning a replacement server/share.
- `cli_dfs_target_check()` strips DFS prefixes for APIs such as rename and hardlink where Windows/NetApp expect target-local paths.
- `smb1_dfs_share_path()` converts paths to DFS-root full paths for SMB1 operations against DFS shares.

Supporting helpers include `cli_cm_force_encryption_creds()`, `cli_cm_find()`, `split_dfs_path()`, `clean_path()`, `cli_dfs_make_full_path()`, `cli_dfs_is_already_full_path()`, `cli_conn_have_dfs()`, and `cli_cm_display()`.

## Control Flow

Connection opening starts in `cli_cm_open()`. A cache hit returns an existing `cli_state`; a cache miss requires credentials and calls `cli_cm_connect()`. `do_connect()` resolves/transports to the server, negotiates SMB dialects, configures SMB2 credit defaults, authenticates with credentials or anonymous fallback where allowed, and enforces encryption when requested. Before tree connect it asks `cli_check_msdfs_proxy()` whether the share is a DFS proxy. If so, it closes the current connection and recursively connects to the referred server/share.

DFS path resolution in `cli_resolve_path()` first normalizes repeated leading separators and short-circuits if the current tcon is not a DFS-capable share. For DFS shares it builds a full DFS path from `\\server\share\path`, probes with `cli_qpathinfo_basic()`, and treats success or `OBJECT_NAME_NOT_FOUND` as an ordinary path. `PATH_NOT_COVERED` triggers referral lookup through an IPC$ connection to the DFS root. The resolver splits every returned referral, prefers already-cached target connections, then tries referral targets in order. It recomposes the target path from the unconsumed portion plus any referral extrapath, parses a new mount prefix, and recursively resolves nested DFS targets. On success, if the returned target is itself a DFS share, it returns a full DFS path for that root.

Referral parsing reads the server-returned consumed UCS-2 path length, converts it back to the UNIX charset to compute consumed bytes in the caller's path, then iterates referral records. Only version 3 referrals are materialized; unsupported versions are skipped by `ref_size`.

## State and Persistence Behavior

All persistent state is in memory. `cli_state` objects are talloc-owned and linked by Samba's DLIST macros so a root connection can own child DFS referral connections. `cli_cm_find()` searches both directions from an arbitrary list member. Temporary tree connect state is carefully saved and restored by `cli_state_save_tcon_share()` and `cli_state_restore_tcon_share()` while probing IPC$ for proxy referrals. No files or registry state are written by this module.

Encryption state is negotiated on the connection/session/tcon. SMB2 uses session encryption; SMB1 requires UNIX extensions with `CIFS_UNIX_TRANSPORT_ENCRYPTION_CAP` and may temporarily connect IPC$ to query capabilities. Path conversion state depends on `cli->requested_posix_capabilities`, the current remote name, and `cli->share`.

## Dependencies and Integration Points

This file integrates with Samba client connection/session code (`cli_connect_nb`, `smbXcli_negprot`, `cli_session_setup_creds`, `cli_tree_connect_creds`), credentials (`struct cli_credentials`), DFS RPC/trans2 definitions (`msdfs.h`, `trans2.h`), SMB2 ioctl support, UNIX extension helpers, and path query helpers from the libsmb file/query layers. It is consumed by higher-level client APIs that need a `cli_state` for a path and by SMB1 file operations that must wrap names in DFS syntax.

## Risks and Edge Cases

- `cli_resolve_path()` explicitly does not check for DFS referral loops, so pathological referral graphs can recurse until another failure or resource limit.
- Referral parsing is network-input sensitive. It has bounds checks for record headers, node offsets, and result lengths, but malformed referral sizes remain a high-value fuzz target.
- Path handling mixes DFS backslashes, POSIX slash support, wildcard trimming, and consumed-byte calculations after charset conversion. Multibyte path names and wildcard paths need coverage.
- `cli_check_msdfs_proxy()` temporarily swaps tcons. Any future early return must preserve restore/tdis ordering to avoid leaking or losing tree state.
- Encryption behavior differs sharply between SMB1 and SMB2 and between desired and required settings; fallback semantics are security-sensitive.

## Test Signals

Useful tests include DFS root ordinary-path success, `PATH_NOT_COVERED` referral resolution, nested referral chains, cached referral target reuse, unavailable first referral with later fallback, MSDFS proxy share detection, self-referral rejection, SMB1 DFS path wrapping for file calls, POSIX separator support, wildcard path cleanup, previous DFS full-path input, required encryption failure paths, and malformed referral buffer bounds tests.
