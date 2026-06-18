# sources/user-network-fs/samba/source3/modules/vfs_full_audit.c

## Purpose
`vfs_full_audit.c` implements Samba's `full_audit` VFS module, a parseable audit logger for VFS operations. It wraps a broad set of disk, directory, file, stream, ACL, xattr, async, durable-handle, snapshot, DFS, compression, and offload operations, forwards each call to the next VFS module, and logs selected success or failure events to syslog or Samba debug output.

## Important APIs, Types, And Functions
`vfs_op_type` enumerates every auditable operation and must stay in lockstep with `vfs_op_names[]`; `init_bitmap()` panics if this table and enum drift. `struct vfs_full_audit_private_data` stores success/failure bitmaps, syslog facility, priority, whether security descriptors should be SDDL-logged, and whether logging goes to syslog.

Configuration helpers are `audit_syslog_facility()`, `audit_syslog_priority()`, `audit_prefix()`, `log_success()`, `log_failure()`, `errmsg_unix()`, and `errmsg_ntstatus()`. `do_log()` is the central sink: it fetches private data, checks the operation bitmap, expands the configured prefix, formats `ok` or `fail (reason)`, and emits `prefix|operation|status|payload`.

`smb_full_audit_connect()` initializes private data after the lower connect succeeds, opens syslog as `smbd_audit` when enabled, parses `full_audit:success` and `full_audit:failure`, stores the handle data, and logs connect. `vfs_full_audit_fns` registers wrappers for all implemented VFS slots, and `vfs_full_audit_init()` calls `smb_vfs_assert_all_fns()` before registering the module as `full_audit`.

## Control Flow
Most wrappers follow a common pattern: call the corresponding `SMB_VFS_NEXT_*` operation, derive failure text from `errno` or `NTSTATUS`, format the relevant path or operation arguments, call `do_log()`, then return the original result. Path helpers normalize `smb_filename` and `files_struct` values into full SMB paths using a temporary talloc context.

Async wrappers split logging across send and recv phases. `pread`, `pwrite`, `fsync`, `get_dos_attributes`, and `getxattrat` allocate small tevent state structs, log send success or allocation failure, forward to the lower async operation, store the recv result in their completion callback, and log final recv success or failure when the caller receives the request.

Operations with multiple path inputs construct full source/destination names before delegation where possible, such as rename, link, symlink, mkdir, unlink, DFS path operations, and readlink. ACL set can optionally encode the submitted security descriptor with `sddl_encode()` when `full_audit:log_secdesc = true`.

## State And Persistence
The module does not persist audit state in the repository or filesystem. Per-share runtime state is held in the VFS handle as bitmaps and logging options. Its durable output is external logging: syslog by default, or Samba `DEBUG(1)` output when `full_audit:syslog = false`. The temporary global `tmp_do_log_ctx` is used only while formatting log arguments and is freed after each `do_log()` call.

The module intentionally preserves wrapped operation semantics. It generally restores `errno` where post-call logging or path cleanup could disturb the caller-visible error, for example in rename paths. Failed configuration during connect disconnects the lower VFS handle and fails the share connect.

## Dependencies And Integration Points
This file depends on Samba VFS interfaces, loadparm parameter APIs, talloc, bitmap utilities, syslog constants, tevent, NTSTATUS helpers, security descriptor SDDL encoding, file-id formatting, path substitution from `source3/lib/substitute.h`, and many Samba file/ACL/xattr structures. Configuration keys are `full_audit:prefix`, `full_audit:success`, `full_audit:failure`, `full_audit:facility`, `full_audit:priority`, `full_audit:log_secdesc`, and `full_audit:syslog`.

The module is designed to be loaded in a share's `vfs objects` list. It integrates with all lower VFS modules through `SMB_VFS_NEXT_*` calls and with system logging through `openlog()` and `syslog()` when built with syslog support.

## Risks
The enum/name table must remain exactly synchronized or configuration parsing can panic at runtime. Audit selection defaults are security-sensitive: the code uses `"none"` as the local default list passed to `init_bitmap()`, while comments describe success defaulting to no logging and failure defaulting to everything, so effective behavior depends on the loadparm defaults that feed the string lists. Logging can leak filenames, usernames, client IPs, xattr names, and optionally complete security descriptors. Full auditing of high-frequency operations like `readdir`, `pread`, `pwrite`, `getxattrat`, and lock checks can create high syslog volume and noticeable overhead. Some wrappers treat operations without clear failure semantics as success, and some payloads are intentionally terse, so logs are useful for tracing but not a complete semantic record of every parameter.

## Test Signals
Relevant Samba selftests include `samba3.test_vfs_full_audit`, blackbox tests for bad success/failure operation names, and `samba.vfstest.full_audit_segfault`. Good coverage should verify success/failure bitmap parsing for `all`, `none`, negated operations, and invalid names; prefix macro expansion; syslog-disabled debug logging; facility/priority fallback; path formatting for relative names; async send/recv logging; SDDL inclusion when `log_secdesc` is enabled; and that wrapped operations preserve return values and `errno`/`NTSTATUS`.
