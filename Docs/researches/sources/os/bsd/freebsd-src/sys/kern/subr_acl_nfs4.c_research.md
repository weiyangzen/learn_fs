# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_acl_nfs4.c

## Summary
Implements common NFSv4 ACL utilities for FreeBSD filesystems and, in non-kernel builds, libc ACL helpers. It covers access checks, ACL-to-mode synchronization, mode-to-ACL synchronization, inherited ACL construction, trivial ACL detection, and ACL validation.

## Main Responsibilities
- Converts vnode `accmode_t` requests to NFSv4 ACL permission masks.
- Evaluates NFSv4 ALLOW/DENY ACEs against credentials, owner, group, and everyone entries.
- Applies owner and privilege fallback semantics for access checks.
- Synchronizes POSIX mode bits from NFSv4 ACL entries.
- Builds ACLs from mode bits using either legacy draft semantics or PSARC/2010/029-style semantics.
- Computes inherited ACLs for new files/directories.
- Detects trivial ACLs so filesystems can avoid storing unnecessary extended attributes.
- Validates supported NFSv4 ACL tags, ids, permissions, entry types, and flags.

## Key APIs
- `vaccess_acl_nfs4()`: kernel access check for NFSv4 ACLs.
- `acl_nfs4_sync_acl_from_mode()`: updates ACL from mode using the selected semantics.
- `acl_nfs4_sync_mode_from_acl()`: derives mode permission bits from an ACL.
- `acl_nfs4_compute_inherited_acl()`: computes child ACL from a parent ACL and creation mode.
- `acl_nfs4_is_trivial()`: tests whether an ACL is equivalent to a trivial mode-derived ACL.
- `acl_nfs4_check()`: syntactic and feature validation.
- `acl_nfs4_trivial_from_mode_libc()`: non-kernel helper for libc trivial/strip operations.

## Important Behavior
`vaccess_acl_nfs4()` ignores `VSYNCHRONIZE`, maps append requests carefully, lets the file owner read/write ACLs and basic attributes, treats append on non-directories as write data, and distinguishes explicit DENY failures when `VEXPLICIT_DENY` is requested. If ACL evaluation fails, it tries privilege grants such as `PRIV_VFS_LOOKUP`, `PRIV_VFS_EXEC`, `PRIV_VFS_READ`, `PRIV_VFS_WRITE`, `PRIV_VFS_ADMIN`, and `PRIV_VFS_STAT`.

For non-directory execute checks, the access path derives a mode from the ACL and requires at least one execute bit to be set, matching `execve(2)` expectations even for privileged users.

The file contains two mode/ACL algorithms. The legacy draft algorithm can be selected by `vfs.acl_nfs4_old_semantics`; it manipulates existing ACEs, duplicates inherited ACEs, and appends/adjusts a canonical six-entry owner/group/everyone tail. The default PSARC-style path builds semantically equivalent trivial ACLs using a smaller deny/allow structure and inherited non-trivial entries.

Inherited ACL generation deliberately skips inheriting `owner@`, `group@`, and `everyone@` entries in the PSARC path, marks inherited ACEs with `ACL_ENTRY_INHERITED`, clears or preserves inheritance flags based on object type and `NO_PROPAGATE`, and masks some inherited ALLOW permissions according to creation mode.

`acl_nfs4_is_trivial()` computes the mode from the ACL, then compares against a PSARC trivial ACL and a legacy canonical-six trivial ACL.

## Dependencies
Kernel builds depend on vnode, mount, credential/group membership, privilege, sysctl, module, and ACL definitions. Non-kernel builds use libc-facing ACL definitions and `assert()` substitutes for kernel assertions.

## Risks
NFSv4 ACL ordering is semantically significant; changes to ACE insertion, duplication, or inheritance flag handling can change effective permissions. The file intentionally accepts multiple owner/everyone ACE shapes as valid, so validators do not enforce canonicality. The old/new semantic switch means filesystems must be aware that behavior can vary under a runtime sysctl.
