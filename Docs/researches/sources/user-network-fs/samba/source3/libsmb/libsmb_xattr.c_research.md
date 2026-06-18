# sources/user-network-fs/samba/source3/libsmb/libsmb_xattr.c

## Purpose
This file implements libsmbclient extended attribute operations for SMB URLs. It exposes synthetic `system.*` xattrs that map to NT security descriptors and DOS file attributes, plus SMB3.1.1 POSIX information for open files. It is the translation layer between POSIX-style `getxattr`, `setxattr`, `removexattr`, and `listxattr` calls and SMB RPC/security descriptor APIs.

## Important APIs, Types, And Functions
Public entry points are `SMBC_setxattr_ctx`, `SMBC_getxattr_ctx`, `SMBC_fgetxattr_ctx`, `SMBC_removexattr_ctx`, and `SMBC_listxattr_ctx`. Internal helpers include `find_lsa_pipe_hnd`, `convert_sid_to_string`, `convert_string_to_sid`, `parse_ace`, `sec_desc_parse`, `add_ace`, `sort_acl`, `dos_attr_query`, `dos_attr_parse`, `cacl_get`, and `cacl_set`.

The NT security path works with `struct security_descriptor`, `struct security_acl`, `struct security_ace`, `struct dom_sid`, LSA policy handles, and `struct rpc_pipe_client`. The DOS attribute path uses a `struct DOS_ATTR_DESC` populated from `SMBC_getatr` and written through `SMBC_setatr`. `SMBC_fgetxattr_ctx` has special file-handle-only names: `posix.attr.enabled` and `smb311_posix.statinfo`.

## Control Flow
`SMBC_setxattr_ctx` validates an initialized context and parses the SMB URL into server/share/path/user/password. It opens the normal tree connection and, unless disabled by `srv->no_nt_session`, an IPC attribute server for LSA/security descriptor operations. Names under `system.nt_sec_desc.*` are converted into descriptor fragments and sent through `cacl_set`; names under `system.dos_attr.*` are merged into the current DOS attributes and written with `SMBC_setatr`; `system.*` can update both surfaces.

`SMBC_getxattr_ctx` follows the same parse/connect flow, then dispatches supported names to `cacl_get`. `cacl_get` parses exclusion suffixes after `!`, decides whether all, NT-only, ACL-only, or DOS-only data was requested, opens the target with `READ_CONTROL_ACCESS`, queries its security descriptor, formats revision/owner/group/ACEs, queries DOS attributes, and appends formatted fields into the caller buffer or calculates required size when `size == 0`.

`cacl_set` parses ASCII descriptors, resolves DFS/path targets, reads the existing descriptor, mutates it according to mode (`ADD`, `SET`, `REMOVE`, `REMOVE_ALL`, `CHOWN`, `CHGRP`), sorts and deduplicates ACEs, then reopens with `WRITE_DAC_ACCESS | WRITE_OWNER_ACCESS` and calls `cli_set_secdesc`.

`SMBC_fgetxattr_ctx` answers `posix.attr.enabled` from `cli_smb2_fnum_is_posix`, decodes `FSCC_FILE_POSIX_INFORMATION` into a caller-provided `struct stat` plus attrs word for `smb311_posix.statinfo`, and otherwise delegates to path-based `SMBC_getxattr_ctx`.

## State And Persistence
The file mutates remote server state: security descriptors, owners/groups, ACL entries, timestamps, and DOS mode bits. It also caches inability to obtain an NT attribute session by setting `srv->no_nt_session`. Most local allocations are stack-frame talloc allocations. It does not maintain durable local state, but it depends on server cache identity checks after `SMBC_attr_server` because that call can evict the original cached server.

## Dependencies And Integration Points
The implementation integrates libsmbclient URL parsing and server caching (`SMBC_parse_path`, `SMBC_server`, `SMBC_attr_server`), low-level SMB open/query/set calls (`cli_ntcreate`, `cli_query_secdesc`, `cli_set_secdesc`, `cli_close`, `SMBC_getatr`, `SMBC_setatr`), LSA SID/name RPC lookup, security descriptor constructors, and SMB2 POSIX info queries. It relies on Samba configuration such as `lp_winbind_separator()` and `context->internal->full_time_names` to choose legacy or full DOS time xattr names.

## Risks And Edge Cases
The xattr grammar is string-heavy: off-by-prefix errors, mixed legacy/new time names, and exclusion parsing can change behavior. `cacl_set` has complex add/replace semantics and a nested loop that can add all requested ACEs while iterating, so duplicate handling depends on later `sort_acl`. Some paths set `errno = 0` after NT failures, which can obscure diagnostics. NT descriptor operations require a working IPC/LSA pipe; DOS-only operations can still partially succeed when NT operations fail. `SMBC_fgetxattr_ctx` requires the caller to pass exactly `sizeof(struct stat) + 4` for POSIX statinfo but returns only `sizeof(struct stat)`, so callers must know the ABI contract.

## Test Signals
Useful tests include `listxattr` with legacy and full time names, size-query `getxattr` calls, `system.*` with exclusions, owner/group SID vs name conversion, ACL add/replace/remove/remove-all cases, DOS mode/time updates, IPC unavailable fallback behavior, server-cache eviction after `SMBC_attr_server`, SMB3.1.1 POSIX statinfo decoding, and error mapping for too-small buffers, invalid names, invalid descriptors, and unsupported servers.
