# File Research: sources/os/linux/linux-stable/fs/vboxsf/file.c

Implements vboxsf regular-file operations, address-space operations, mmap hooks, symlink readlink support, and host handle lifetime. `struct vboxsf_handle` wraps a host `SHFL` handle, root id, access flags, refcount, and per-inode list linkage.

Open maps Linux open flags to VirtualBox create/access flags, calls `vboxsf_create_at_dentry()`, and stores a newly tracked `vboxsf_handle` in `file->private_data`. Release writes back dirty pagecache with `filemap_write_and_wait()` before closing the host handle so host-side readers see guest writes.

Read and write use generic VFS file helpers backed by `vboxsf_reg_aops`. `vboxsf_read_folio()` reads one page from the host and zero-fills the tail. `vboxsf_writepages()` finds an open write-capable handle and writes dirty folios back. `vboxsf_write_end()` writes only copied bytes and extends inode size if needed. mmap uses `filemap_fault` and flushes dirty pages when the VMA closes.

A large comment documents the caching model: host-side changes can occur without notification, so the driver only guarantees seeing host changes made before guest open/revalidation. Symlinks are read through `vboxsf_readlink()`.
