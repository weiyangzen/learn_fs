<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/access_check.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/access_check.c

## Purpose

This file provides common FSAL access checking for NFS-Ganesha objects. It evaluates NFSv4 ACLs or POSIX mode bits against `op_ctx->creds`, formats ACL/access data for logs, and manages process/thread credentials used by local-filesystem FSALs.

## Important APIs, Types, and Functions

- ACE matching helpers: `fsal_check_ace_owner`, `fsal_check_ace_group`, `fsal_check_ace_matches`, and `fsal_check_ace_applicable`.
- ACL/mask formatting: `fsal_ace_type`, `fsal_ace_perm`, `fsal_ace_flag`, `fsal_print_ace_int`, `fsal_print_acl_int`, `display_fsal_inherit_flags`, `display_fsal_ace`, and `display_fsal_v4mask`.
- Access evaluation: `fsal_check_access_acl`, `fsal_check_access_no_acl`, and public `fsal_test_access`.
- Credential switching: `fsal_set_credentials`, `fsal_restore_ganesha_credentials`, `fsal_set_credentials_only_one_user`, and `fsal_save_ganesha_credentials`.
- Global credential state: `ganesha_uid`, `ganesha_gid`, `ganesha_ngroups`, and `ganesha_groups`.

## Control Flow

`fsal_test_access` determines whether ACL data is needed from the requested access flags, fetches required attributes with `getattrs`, optionally grants owner skip, then chooses ACL evaluation if ACLs are required or available for a v4 mask; otherwise it falls back to POSIX mode-bit evaluation. ACL evaluation handles root specially, grants owner read/write ACL and attr privileges, walks ACEs in order, applies only matching and object-applicable allow/deny ACEs, tracks remaining requested access, and returns either success, access denied, permission denied, or no matching ACE. Mode evaluation selects owner, group, alternate group, or other bits, handles root execute semantics, and computes allowed/denied masks.

## State and Persistence Behavior

The access checks themselves are stateless aside from logs and temporary attr allocation/release. Credential helpers persist the server's original uid/gid/group list in globals and can mutate thread credentials on platforms with `GSH_CAN_HOST_LOCAL_FS`.

## Dependencies and Integration Points

This file relies on `op_ctx`, `op_ctx->fsal_export->exp_ops.is_superuser`, FSAL attr and ACL structures, NFSv4 ACL macros, display/logging utilities, and OS credential helpers from `os/subr.h`. It is the default object `test_access` implementation used by FSALs unless overridden.

## Risks and Edge Cases

- ACL behavior differs under `ENABLE_RFC_ACL`; without it, some denied ACL administrative bits return `ERR_FSAL_PERM` rather than `ERR_FSAL_ACCESS`.
- Root is allowed all directory access and all file access except execute unless an execute bit/ACE path grants it.
- `fsal_ace_perm` uses a static buffer, so it is not reentrant across concurrent formatting in the same expression.
- Missing ACL with `FSAL_ACE4_REQ_FLAG` returns `ERR_FSAL_NO_ACE`, which callers such as delete/rename helpers interpret specially.
- Credential switching failures are fatal, so local FSALs must pass valid groups.

## Test Signals

High-value tests include owner/group/everyone ACE allow/deny ordering, inherit-only and file-vs-directory applicability, root file execute denial, owner implicit ACL/attr rights, `FSAL_ACE4_REQ_FLAG` no-ACL behavior, POSIX mode fallback for primary and supplementary groups, and credential save/restore on supported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/access_check.c -->
