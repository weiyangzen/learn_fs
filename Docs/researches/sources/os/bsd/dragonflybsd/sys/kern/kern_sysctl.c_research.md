# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sysctl.c

## Purpose

`kern_sysctl.c` implements DragonFlyBSD's kernel sysctl MIB tree: static and dynamic OID registration, dynamic context cleanup, name/OID discovery nodes, default scalar/string/opaque handlers, kernel and user request transfer routines, syscall entry, sbuf draining, and global sysctl topology locking.

## MIB Tree Management

- `sysctl_find_oidname()` searches a sibling list by name.
- `sysctl_register_oid()` and `sysctl_register_oid_int()` initialize per-OID locks, reuse existing nodes by incrementing refcounts, assign `OID_AUTO` numbers starting at `0x100`, and insert OIDs sorted by number.
- `sysctl_unregister_oid()` and `sysctl_unregister_oid_int()` remove registered non-`OID_AUTO` OIDs.
- `sysctl_register_all()` registers static OIDs from `sysctl_set` during boot.
- `sysctl_rename_oid()` replaces an OID name under the sysctl topology lock.

## Dynamic Contexts And Removal

- `sysctl_ctx_init()` initializes a context list.
- `sysctl_ctx_entry_add()`, `sysctl_ctx_entry_find()`, and `sysctl_ctx_entry_del()` manage dynamic context membership.
- `sysctl_ctx_free()` performs a dry-run deregistration of all context entries, restores them if any removal fails, then deletes entries for real.
- `sysctl_remove_oid()` and `sysctl_remove_oid_locked()` remove dynamic OIDs, optionally recursively, reject non-dynamic OIDs, decrement shared-node refcounts, mark dying OIDs, wait for running handlers to drain, and free dynamic name/description/children/OID storage when requested.
- `sysctl_remove_name()` removes a child by name.
- `sysctl_add_oid()` dynamically creates or reuses an OID, allocates child lists for nodes, copies name/description storage, links into optional context, and registers it.

## Discovery And Default Handlers

- Sysctl discovery:
  - `sysctl_sysctl_name()` maps numeric OIDs to dotted names.
  - `sysctl_sysctl_next_ls()` and `sysctl_sysctl_next()` find the next visible OID.
  - `name2oid()` and `sysctl_sysctl_name2oid()` map dotted names to numeric OID arrays.
  - `sysctl_sysctl_oidfmt()` returns kind/format metadata.
  - `sysctl_sysctl_oiddescr()` returns descriptions.
  - Optional `SYSCTL_DEBUG` support dumps the tree.
- Default value handlers:
  - `sysctl_handle_8()`, `sysctl_handle_16()`, `sysctl_handle_32()`, `sysctl_handle_64()`, `sysctl_handle_int()`, `sysctl_handle_long()`, `sysctl_handle_quad()`, `sysctl_handle_bit32()`, and `sysctl_handle_bit64()` implement common scalar read/write behavior.
  - `sysctl_handle_string()` handles NUL-terminated writable strings with length checking.
  - `sysctl_handle_opaque()` copies fixed-size opaque payloads.
  - `sysctl_int_range()` validates integer updates against a caller-provided range.

## Request Execution

- Transfer helpers:
  - `sysctl_old_kernel()`/`sysctl_new_kernel()` copy to/from kernel buffers.
  - `sysctl_old_user()`/`sysctl_new_user()` copy to/from user buffers.
- Kernel entry:
  - `kernel_sysctl()` builds a kernel-backed `sysctl_req`, runs `sysctl_root()` under shared sysctl lock, and reports actual/valid old length.
  - `kernel_sysctlbyname()` resolves a dotted name through `CTL_SYSCTL_NAME2OID`, then performs the target sysctl.
- User entry:
  - `sys___sysctl()` copies in the numeric name, calls `userland_sysctl()`, and copies out the resulting length.
  - `userland_sysctl()` builds a user-backed request, optionally emits KTRACE, retries `EAGAIN`, and reports returned length.
- `sysctl_find_oid()` walks numeric OIDs to a leaf or handler node and rejects non-directory continuations.
- `sysctl_root()` validates write permissions, securelevel, root/capability requirements, handler presence, OID lock mode, and invokes the handler with either remaining path components for node handlers or stored args for leaf handlers.
- `sbuf_new_for_sysctl()` creates an sbuf with a drain callback that writes through `SYSCTL_OUT()`.

## Locking Model

The topology lock is implemented as per-CPU `gd_sysctllock` locks. `_sysctl_xlock()` takes every CPU lock exclusively for topology mutation; normal sysctl traversal uses shared locking through macros. Individual OIDs also have per-OID locks, with default read-shared/write-exclusive behavior unless `CTLFLAG_NOLOCK`, `CTLFLAG_SHLOCK`, or `CTLFLAG_EXLOCK` overrides it.

## Risks And Invariants

Dynamic removal is delicate because handlers can run while modules unload; `oid_running` draining and `CTLFLAG_DYING` preserve the prior behavior of holding the global lock across handlers. Name-to-OID parsing mutates a copied string with `strsep()`. `sysctl_handle_string()` assumes `arg1` is a valid writable buffer of size `arg2` for writes. Permission checks distinguish readable public discovery nodes from writes guarded by capability and securelevel rules.
