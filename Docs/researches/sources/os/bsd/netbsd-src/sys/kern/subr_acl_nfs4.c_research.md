# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_acl_nfs4.c

Read completely: 620 lines.

Provides shared utility routines for filesystems implementing NFSv4 ACLs. The file supports both kernel builds and a libc-oriented non-kernel build path for trivial ACL construction used by ACL library helpers.

Core helpers:
- `_acl_append()` appends an ACL entry with a tag, permissions, entry type, undefined ID, and zero flags.
- `acl_nfs4_trivial_from_mode()` builds a trivial ACL from a POSIX mode using the PSARC/2010/029-compatible inherited ACL algorithm.
- `acl_nfs4_sync_acl_from_mode()` is the kernel entry point for rebuilding an ACL from mode bits; the current `file_owner_id` parameter is unused.
- `__acl_nfs4_trivial_from_mode_libc()` exposes the trivial-mode builder to libc when `_KERNEL` is not defined.

Mode reconstruction:
- `__acl_nfs4_sync_mode_from_acl()` walks non-inherit-only ALLOW/DENY ACEs and derives user/group/other read, write, and execute mode bits.
- It handles `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, and `ACL_EVERYONE`; `ACL_EVERYONE` can populate still-unseen user, group, and other bits.
- First-seen semantics matter: a permission bit is marked seen whether an ALLOW or DENY entry caused it; only ALLOW adds the corresponding mode bit.
- Non-permission bits preserved by `ACL_PRESERVE_MASK` are copied from the original mode.

Inheritance:
- `acl_nfs4_inherit_entries()` copies inheritable non-owner/group/everyone ACEs from a parent ACL into a child ACL.
- It filters by `ACL_ENTRY_FILE_INHERIT`, `ACL_ENTRY_DIRECTORY_INHERIT`, object type, and `ACL_ENTRY_NO_PROPAGATE_INHERIT`.
- Inherited entries are marked `ACL_ENTRY_INHERITED` and generally have `ACL_ENTRY_INHERIT_ONLY` cleared unless directory/file inheritance rules require it.
- ALLOW entries that apply to the new object have permissions masked: some permissions are never inherited, and read/write/execute data permissions are limited according to group mode bits.

PSARC-style ACL construction:
- `acl_nfs4_compute_inherited_acl_psarc()` derives base `user_allow`, `group_allow`, and `everyone_allow` permission masks from the requested mode.
- It grants common metadata permissions to all three classes and adds write-owner/ACL/attribute permissions to the owner.
- It computes owner and group DENY entries needed to prevent broader group/everyone permissions from exceeding narrower owner/group permissions.
- It optionally appends inherited parent ACEs before appending final owner, group, and everyone ALLOW ACEs.
- `acl_nfs4_compute_inherited_acl()` is the kernel wrapper around this PSARC-compatible implementation.

Triviality and validation:
- `_acls_are_equal()` compares ACL count and all ACE fields exactly.
- `acl_nfs4_is_trivial()` computes mode from the ACL, rebuilds a trivial ACL from that mode, and compares for equality; it immediately rejects ACLs with more than six entries.
- `acl_nfs4_check()` validates count, tag/id combinations, allowed NFSv4 permission bits, ALLOW/DENY entry types, allowed flags, unsupported audit/alarm flags, and inheritance flags on non-directories.

Risks and notes:
- Several commented-out helpers and comments reference alternate canonical-six trivial ACL logic, but the implemented triviality check only returns the PSARC comparison result.
- ACL validity is intentionally permissive about multiple or missing owner/group/everyone entries because NFSv4 permits more flexible ACL forms.
- `file_owner_id` is currently unused in exported functions, so owner-specific inheritance policy is not represented here.
- `__acl_nfs4_sync_mode_from_acl()` depends on ACE order; reordering semantically similar ACLs can change reconstructed mode bits.
