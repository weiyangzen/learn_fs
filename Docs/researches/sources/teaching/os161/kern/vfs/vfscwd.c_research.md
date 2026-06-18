# File Research: sources/teaching/os161/kern/vfs/vfscwd.c

Implements current-working-directory operations. `vfs_getcurdir` takes `curproc->p_lock`, increfs `p_cwd` if present, and returns `ENOENT` otherwise. `vfs_setcurdir` verifies the vnode type is `S_IFDIR`, increfs the new directory, swaps it under the process lock, then decrefs the old directory. `vfs_clearcurdir` clears and releases the old reference.

`vfs_chdir` resolves a pathname with `vfs_lookup`, installs it with `vfs_setcurdir`, and drops the lookup reference. `vfs_getcwd` writes `volume-or-device-name:` followed by `VOP_NAMEFILE(cwd, uio)`.

The code depends on balanced vnode references and assumes current directories are filesystem-backed, not device vnodes.
