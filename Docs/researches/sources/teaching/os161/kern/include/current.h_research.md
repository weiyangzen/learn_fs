# File Research: sources/teaching/os161/kern/include/current.h

Defines machine-dependent access to current CPU/thread and machine-independent `curproc`.

Key behavior:
- Includes `<machine/current.h>`, which chooses whether `curcpu` or `curthread` is primary.
- If `__NEED_CURTHREAD`, defines `curthread` via `curcpu->c_curthread`.
- If `__NEED_CURCPU`, defines `curcpu` via `curthread->t_cpu`.
- Defines `curproc` as `curthread->t_proc`.

Relevance:
- `semfs_vnops.c` includes current/process headers as part of vnode operation context.
- VFS/syscall code commonly relies on `curproc->p_cwd`.
