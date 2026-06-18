# sources/user-network-fs/samba/source3/smbd/proto.h

## Purpose
This header is the broad internal prototype map for source3 smbd. It gathers declarations from many smbd compilation units so legacy and cross-module C code can call server routines for signing, async I/O, byte-range locking, connection management, DOS mode handling, path resolution, file table operations, notifications, quotas, ACLs, SMB packet processing, encryption, security context switching, service/session management, VFS helpers, and SMB2 create support.

## Important APIs, Types, And Functions
The header forward-declares major server types such as `smbXsrv_client`, `smbXsrv_connection`, `dcesrv_context`, and several operation-specific structs. It exposes grouped declarations by implementation file. For this work item, the important groups are `posix_acls.c` (`posix_fget_nt_acl`, `set_nt_acl`, `set_unix_posix_acl`, default ACL helpers), `quotas.c` (`disk_quotas`), and `seal.c` (`is_encrypted_packet`, `srv_decrypt_buffer`, `srv_encrypt_buffer`, `srv_request_encryption_setup`, `srv_encryption_start`, `server_encryption_shutdown`). It also declares the adjacent dependencies those files use, including pathref open/close helpers, security context helpers, VFS operations, and SMB request processing entry points.

## Control Flow
`proto.h` has no runtime control flow. Its compile-time organization mirrors smbd subsystems, with comments identifying the source file for each declaration block. Include guards prevent repeated declarations, and conditional blocks expose quota query helpers only when `HAVE_SYS_QUOTAS` or SMB1-server build choices make them valid.

## State And Persistence
The header stores no runtime state and persists no data. Its practical state is C ABI coupling: signatures here must match definitions exactly, and any mismatch can become compiler warnings, link errors, or undefined behavior depending on build flags.

## Dependencies And Integration Points
Because this is a central smbd header, it integrates almost every file-server subsystem. It relies on types from `smbd.h`, Samba security/ACL headers, tevent, messaging, VFS, locking, notify, and SMB request structures being available through normal include chains. Changes to declarations here affect call sites throughout source3 and, for non-static functions, the internal module boundary.

## Risks And Test Signals
Risks are stale prototypes after implementation changes, accidental exposure of functions that should stay file-local, conditional declaration drift across build configurations, and ABI mismatches for structs or enum types declared elsewhere. Test signals are full matrix compilation with SMB1 enabled/disabled, quota support enabled/disabled, POSIX ACL support enabled/disabled, and warning-clean builds that include call sites for ACL, quota, seal, VFS, and SMB2 create paths.
