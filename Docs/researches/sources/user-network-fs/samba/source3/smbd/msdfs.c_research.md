# sources/user-network-fs/samba/source3/smbd/msdfs.c

## Purpose
`msdfs.c` implements source3 smbd support for Microsoft DFS referrals. It parses DFS paths, builds temporary VFS connections for referral lookup, parses and emits Samba's `msdfs:` symlink format, detects MSDFS links, resolves a DFS path to referral targets, and serializes referral replies for TRANS2/FSCTL callers.

## Important APIs, Types, And Functions
`parse_dfs_path_strict()` parses `\\server\\share` and `\\server\\share\\remaining` paths, verifies the hostname belongs to this server, and returns hostname/share/remaining components. `create_conn_struct_chdir()` wraps `create_conn_struct_as_root()` and returns a `conn_wrap` whose destructor disconnects VFS state and resets cwd/chdir cache. `parse_msdfs_symlink()` parses `msdfs:server\\share,...` or slash variants into `struct referral` arrays and optional shuffled order. `is_msdfs_link()` asks the VFS to read DFS path data at a dirfsp-relative name. `get_referred_path()` is the main referral resolver. `setup_dfs_referral()` invokes VFS referral generation and NDR-marshals the response. `msdfs_link_string()` formats referrals back into a storable `msdfs:` string.

## Control Flow
Strict parsing copies the path, requires an initial backslash, splits hostname and share on backslashes, checks `is_myname_or_ipaddr()`, and leaves remaining path syntax validation to the caller. Referral lookup starts in `get_referred_path()`: parse the DFS path, reject invalid syntax, normalize the service name, verify the share is a DFS root or proxy, and handle self-referral or proxy-target referral without opening the share path. For non-root paths, it creates a temporary connection to the share as the caller session, copies remote/local addresses if missing, and calls `dfs_path_lookup()`.

`dfs_path_lookup()` converts the requested path with `filename_convert_dirfsp()`. When conversion returns `NT_STATUS_PATH_NOT_COVERED`, it strips one component and retries until a covered parent is found. It then resolves the real last component name under the parent, asks `SMB_VFS_READ_DFS_PATHAT()` for referrals, and computes how many bytes of the canonical DFS path were consumed by removing the still-unconsumed path components from the original DFS path.

## State And Persistence
This file creates transient `connection_struct` and `smbd_server_connection` objects for referral lookup. `parse_msdfs_symlink()` and `msdfs_link_string()` operate on in-memory referral structures but encode/decode the persistent Samba MSDFS symlink payload format. The temporary connection destructor calls `SMB_VFS_DISCONNECT()`, frees the connection, `chdir("/")`, and resets the chdir cache to make unmounts possible.

## Dependencies And Integration Points
`msdfs.c` depends on loadparm share settings (`msdfs root`, `msdfs proxy`, shuffle referrals, share paths), authentication/session info, VFS connect/read-dfs hooks, global messaging context, DFS NDR blobs, `filename.c` path conversion, `get_real_filename_at()` for case-correct link names, and `conn_new`/VFS initialization. It integrates with trans2/FSCTL referral reply generation through `SMB_VFS_GET_DFS_REFERRALS()` and `ndr_push_dfs_referral_resp`.

## Risks
Security-sensitive areas include hostname validation, share access checks during fake connection creation, root privilege boundaries around VFS connect, cwd changes in a server process, DFS proxy target parsing, and path-consumed length calculation. Referral resolution depends on path conversion returning `PATH_NOT_COVERED` only for DFS links; other errors abort. Component stripping has mismatch and integer-wrap checks, but malformed paths and path separator normalization remain high-value tests.

## Test Signals
Tests should cover strict DFS parsing, nonlocal host rejection, missing share rejection, invalid remaining path syntax, service alias resolution, non-DFS share rejection, DFS root self-referral, DFS proxy referral, shuffled referral order, slash and backslash symlink target canonicalization, max referral count, empty referral entries, temporary connection access denied/read-only paths, `PATH_NOT_COVERED` walkback through nested paths, consumed-count calculation, GMT token handling inside lookup, VFS read failures, NDR marshal failures, and `msdfs_link_string()` formatting/trimming.
