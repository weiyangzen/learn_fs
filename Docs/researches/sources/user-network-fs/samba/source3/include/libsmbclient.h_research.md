# sources/user-network-fs/samba/source3/include/libsmbclient.h

## Purpose
This is the public C ABI for Samba's `libsmbclient` library. It exposes URL-oriented SMB/CIFS client operations for files, directories, attributes, notifications, printing, context configuration, authentication, server caching, credentials fallback, thread hooks, URL encoding, and version discovery. The header is deliberately ABI-conservative: the visible `SMBCCTX` struct remains for old applications, but comments direct new code to getter/setter APIs and internal private state.

## Important APIs, Types, And Control Flow
Core opaque handles are `SMBCCTX`, `SMBCSRV`, and `SMBCFILE`. Public data structures include `struct smbc_dirent`, `struct libsmb_file_info`, print job metadata, notification callback action arrays, and enums for share modes, SMB encryption level, VFS feature bits, directory entry kinds, DOS mode xattr bits, and xattr create/replace flags. The control surface appears in two layers: context methods such as `smbc_getFunctionOpen()`/`smbc_setFunctionOpen()` install operation callbacks, while compatibility functions such as `smbc_open()`, `smbc_read()`, `smbc_opendir()`, `smbc_stat()`, `smbc_setxattr()`, and `smbc_print_file()` dispatch through the active context.

## State And Persistence
State lives in a context and its internal data: debug settings, NetBIOS name, workgroup, user, timeout, TCP port, protocol bounds, Kerberos and ccache flags, encryption level, browse behavior, URL encoding behavior, server cache callbacks, open handles, and private user data. The library persists no files directly through this header, but operations mutate remote SMB servers, remote ACLs and extended attributes, print queues, connection caches, and optional global credentials used for DFS referrals.

## Dependencies And Integration Points
The header depends on POSIX stat/statvfs, fcntl, time, utime, and Samba implementation files in `libsmbclient.c`, `libsmb_context.c`, `libsmb_dir.c`, `libsmb_file.c`, cache code, auth callbacks, DFS referral handling, and SMB protocol negotiation. It integrates with consumers as a stable installed header and with Samba internals through the private `SMBC_internal_data` pointer.

## Risks And Test Signals
Risks include old applications directly mutating deprecated struct fields, global configuration side effects from log and configuration setters, ambiguity around URL-encoded directory entries, credential fallback accidentally enabling anonymous access, xattr security descriptor parsing errors, thread hook misuse, and ABI breakage if fields are reordered. Test signals include ABI compile tests, context lifecycle and cleanup tests, file and directory round trips against an SMB server, DFS referral access, Kerberos/NTLM fallback combinations, xattr ACL get/set/list/remove, notifications, print queue calls, custom server cache callbacks, and multithreaded context use after `smbc_thread_posix()` or `smbc_thread_impl()`.
