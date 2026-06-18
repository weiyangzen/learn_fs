# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_module_vfs.c

## Purpose
Connects the module subsystem to VFS-backed files: loads `.kmod` kernel objects and optional `.plist` property files from module paths.

## Main Interfaces
- `module_load_vfs_init`: installs `module_load_vfs` into `module_load_vfs_vec` and prints `kern.module.path`.
- `module_load_vfs(name, flags, autoload, mod, filedictp)`: resolves explicit or autoload paths, invokes `kobj_load_vfs`, optionally loads plist properties, enforces `noautoload`, and returns a property dictionary when requested.

## Internal Helpers
- `module_load_plist_vfs(modpath, nochroot, filedictp)`: derives `.plist` path, opens vnode, stats size, reads up to 8191 bytes into kernel memory, NUL-terminates, and internalizes as a proplib dictionary.

## Dependencies
- VFS/namei/vnode routines: `vn_open`, `vn_stat`, `vn_rdwr`, `vn_close`, `VOP_UNLOCK`.
- Module/kobj APIs: `kobj_load_vfs`, `kobj_unload`, `module_print`, `module_error`.
- `PNBUF_GET/PUT`, `pathbuf_create/destroy`, proplib dictionaries, `curlwp` credentials.

## Control Flow Notes
- Non-autoload with a slash loads the exact path under current root/chroot rules.
- Autoload or fallback `ENOENT` with a plain name loads `${module_base}/${name}/${name}.kmod` with `NOCHROOT`.
- Plist loading is skipped when `MODCTL_NO_PROP` is set unless autoload needs to check `noautoload`.
- On plist error other than `ENOENT`, loaded kobj is unloaded.

## Risk Areas
- Plist files larger than 8191 bytes return `EFBIG`.
- Autoload property `noautoload=true` blocks loading with `EPERM`.
- Path handling intentionally disallows fallback in cases with unexpected slashes.
- The file assumes the vnode remains locked after `vn_open` and unlocks before close.

## Filesystem Relevance
Direct. This is the VFS-facing half of kernel module loading and exercises pathname resolution, vnode I/O, credentials, and chroot bypass policy.
