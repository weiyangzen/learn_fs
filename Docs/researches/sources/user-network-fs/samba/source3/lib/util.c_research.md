<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util.c -->
# sources/user-network-fs/samba/source3/lib/util.c

## Purpose
`util.c` is a broad source3 utility collection. It contains legacy SMB message helpers, path cleanup, process-after-fork reinitialization, account/group conversion helpers, panic-action handling, path/name matching, lock probing, remote client architecture tracking and caching, safe buffer pointer helpers, old OpenX-to-NTCreate mapping, Unix token copying, and directory search attribute filtering.

## Important APIs, types, and functions
Important functions include `set_Protocol`, `gfree_all`, `file_exist_stat`, `socket_exist`, `show_msg`, `set_message_bcc`, `message_push_blob`, `unix_clean_name`, `clean_name`, `write_data_at_offset`, `init_before_fork`, `parent_watch_fd`, `reinit_after_fork`, `add_to_large_array`, `uidtoname`, `gidtoname`, `nametouid`, `nametogid`, `smb_panic_s3`, `is_in_path`, `fcntl_getlock`, `map_process_lock_to_ofd_lock`, `is_myname`, remote-architecture getters/setters/cache functions, `set_maxfiles`, `smb_xmalloc_array`, `myhostname`, `parent_dirname`, `ms_has_wild`, `mask_match`, `is_offset_safe`, `get_safe_str_ptr`, `split_domain_user`, `map_open_params_to_ntcreate`, `copy_unix_token`, `root_unix_token`, and `dir_check_ftype`.

## Control flow
Fork setup creates a pipe before fork; children close the write end, reinitialize tdb, tevent tracing, messaging, and CTDB async context, then watch the read end so EOF terminates child processes when the parent exits. Remote architecture flow sets a global enum from LanMan strings or cache entries keyed by client GUID, using root privilege for gencache access. Open mapping translates DOS deny/open modes into NT access, share mode, create disposition, options, and private deny flags. Path utilities normalize `.` and `..`, parse parent/name components, and perform Microsoft wildcard matching using the configured SMB protocol.

## State and persistence behavior
Process-global state includes `Protocol`, remote architecture `ra_type`, cached hostname strings, and fork pipe file descriptors. Remote architecture data is persisted in Samba gencache for seven days. Some helpers temporarily become root for panic action or gencache updates. Other functions operate only on caller-owned buffers or talloc allocations.

## Dependencies and integration points
The file integrates with loadparm, char conversion, interfaces, debug/memcache cleanup, TDB/CTDB, messaging, server ID databases, gencache, passwd/group APIs, SMB protocol field macros, locking syscalls, wildcard matching, and security token definitions. It is shared across smbd, winbindd, client, and VFS-facing code.

## Risks and edge cases
This file has high blast radius because many helpers are old compatibility surfaces. SMB message functions assume valid SMB1 buffer layout. `add_to_large_array` signals allocation failure by setting array size to `-1`. Remote architecture cache requires privilege transitions and validates null-terminated cache blobs. `is_offset_safe` must catch pointer arithmetic wrap. `map_open_params_to_ntcreate` encodes subtle DOS deny semantics, especially executable handling under `DENY_DOS`.

## Test signals
Useful coverage includes fork reinit behavior, open-mode mapping matrices, path cleanup edge cases, wildcard protocol behavior, safe-buffer wrap checks, remote arch cache set/get/delete, file lock probing, and directory attribute filtering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util.c -->
