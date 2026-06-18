# File Research: sources/teaching/minix/minix/servers/vfs/protect.c

Implements protection-related syscalls and generic vnode access checks.

Key behavior:
- `do_chmod` handles path and fd variants, requires owner or superuser, rejects read-only filesystems, clears setgid for non-superusers outside the file's group, calls `req_chmod`, and updates cached vnode mode.
- `do_chown` handles path and fd variants, rejects read-only filesystems, restricts non-superusers from giving away files or changing to arbitrary groups, calls `req_chown`, and updates cached uid/gid/mode.
- `do_umask` updates `fp_umask` and returns the complement of the old mask.
- `do_access` validates requested access bits, resolves the path using real uid/gid semantics through `forbidden`, and returns the permission result.
- `forbidden` computes access from owner/group/supplementary group/other bits, gives superuser read/write plus directory search and conditional execute, and checks read-only mounts for write access.
- `read_only` tests `vp->v_vmnt` for `VMNT_READONLY`.

Important dependencies:
- Path operations use `lookup_init` and `eat_path`.
- Permission state comes from `fproc`, vnode metadata, and supplementary group helper `in_group`.
- Metadata updates are delegated to filesystem servers through `req_chmod` and `req_chown`.

Notable detail:
- For `VFS_ACCESS`, both path lookup credentials and `forbidden` use real uid/gid instead of effective uid/gid.
