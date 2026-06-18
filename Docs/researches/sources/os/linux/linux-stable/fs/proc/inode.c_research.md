# File Research: sources/os/linux/linux-stable/fs/proc/inode.c

Implements procfs inode allocation, eviction, superblock operations, proc_dir_entry lifetime protection, and generic file-operation dispatch for regular proc entries.

Key points:
- Defines `proc_sops`, backed by proc-specific inode slab allocation/freeing.
- `proc_evict_inode()` tears down PID tracking and sysctl inode associations.
- `proc_invalidate_siblings_dcache()` invalidates dentries tied to sysctl/PDE sibling inode lists across superblocks.
- Uses `proc_dir_entry::in_use` with a negative bias to block new users during removal.
- Tracks open files with custom release hooks via `struct pde_opener`, allowing `remove_proc_entry()` and last close to coordinate exactly one `proc_release()`.
- Wraps `proc_ops` methods for read, read_iter, write, poll, ioctl, compat ioctl, mmap, get_unmapped_area, open, release, and lseek.
- Permanent PDEs bypass runtime `use_pde()` accounting for faster static entries.
- `proc_get_inode()` materializes VFS inodes from PDE metadata and selects file ops based on type, read_iter, and compat ioctl flags.

Dependencies/contracts:
- Consumes `struct proc_dir_entry`, `struct proc_inode`, and `struct pde_opener` from `internal.h`.
- Calls PID cleanup from proc base code and sysctl cleanup from `proc_sysctl.c`.
- Central lifetime layer for dynamically registered proc files.
