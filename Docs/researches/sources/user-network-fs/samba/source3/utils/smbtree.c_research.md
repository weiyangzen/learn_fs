# sources/user-network-fs/samba/source3/utils/smbtree.c

## Purpose

`sources/user-network-fs/samba/source3/utils/smbtree.c` implements the `smbtree` network-neighborhood browser. It enumerates workgroups, servers, and optionally shares through libsmbclient using `smb://` directory traversal. The source was read as a complete 299-line file.

## Important APIs, Types, and Functions

The executable has `main`, an auth callback `get_auth_data_with_context_fn`, enum `tree_level` (`LEV_WORKGROUP`, `LEV_SERVER`, `LEV_SHARE`), and global `level`. It configures `SMBCCTX`, uses libsmbclient function slots such as `Opendir`, `Readdir`, and `Closedir`, and consumes credentials from `samba_cmdline_get_creds`.

## Control Flow

`main` initializes locale, stdout buffering, Samba client command-line parsing, and popt options. `--domains` stops at workgroups, `--servers` stops at server listing, and the default includes shares. After building an `SMBCCTX`, it points the configuration at `smb.conf`, preserves the debug level, forces the protocol max/min option to `"NT1"`, installs the auth callback, and initializes the context. It opens `smb://`, prints workgroup names, recursively opens `smb://WORKGROUP/` for servers, and opens `smb://SERVER/` for shares.

## State and Persistence Behavior

The program has no durable state. Runtime state is the libsmbclient context, active directory handles, command-line credentials, and talloc strings for URLs/server names. Output is printed directly to stdout.

## Dependencies and Integration Points

It depends on libsmbclient, Samba cmdline credentials, `smb.conf`, NetBIOS name browsing, the srvsvc/RPC and namequery stack, and SMB1/NT1 browsing behavior. The error message explicitly documents that the utility does not work when NetBIOS name resolution is not configured and that SMB2/SMB3 browsing via WSD/LLMNR is not supported here.

## Risks and Edge Cases

The core behavior depends on SMB1/NetBIOS browsing, which is disabled in many modern environments. A failed nested `opendir` aborts the whole command rather than skipping only the failing workgroup/server. The auth callback silently returns if fixed-size output buffers are too small. Directory-entry storage can be overwritten by nested readdir calls, so the code copies server names before opening shares.

## Test Signals

Tests should cover option parsing levels, credential callback truncation behavior, empty/failed `smb://` root browsing, server/share enumeration with a mock or test libsmbclient server, and environments where NT1 browsing is disabled.
