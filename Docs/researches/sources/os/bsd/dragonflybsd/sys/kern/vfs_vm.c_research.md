# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vm.c

## Role

This file implements newer VFS/VM coherency helpers for truncating and extending vnode-backed files. It keeps VM object sizing aligned with the final buffer cache buffer rather than the exact byte EOF, simplifying interactions for filesystems with fixed-size or offset-based buffers such as NFS and HAMMER.

## Main Responsibilities

- Provides `nvtruncbuf()` for truncation:
  - Computes the logical offset beyond which buffers must be destroyed.
  - Removes clean and dirty buffers beyond the new EOF-covering buffer.
  - Calls `nvnode_pager_setsize()` to update vnode and VM object size.
  - Zero-fills the portion of the last buffer beyond EOF unless `NVEXTF_TRIVIAL` is set.
  - Optionally writes the zero-filled buffer with `buwrite()` when `NVEXTF_BUWRITE` is set, otherwise uses `bdwrite()`.
  - Fsyncs remaining metadata buffers with negative logical offsets for nonzero truncations.
  - Waits for tracked writes and repeats cleanup to catch buffers instantiated by concurrent VM/page activity.
- Provides `nvextendbuf()` for extension:
  - Updates VM object sizing with `nvnode_pager_setsize()`.
  - Zero-fills the old EOF-straddling buffer unless `NVEXTF_TRIVIAL` is set.
  - Clears cached raw disk offsets so future writes remap correctly.
- Provides `nvnode_pager_setsize()`:
  - Updates `vp->v_filesize`.
  - Sets `vp->v_object->size` to include the last buffer containing EOF.
  - Removes VM pages beyond the last EOF-covering buffer on shrink.
  - Unmaps user-visible pages beyond the byte-granular EOF while preserving pages still covered by the last buffer.

## Synchronization and Lifetime Model

- `nvtruncbuf()` takes `vp->v_token` while scanning buffer trees.
- Buffer callbacks lock each buffer, revalidate clean/dirty state, vnode ownership, and logical offset after lock acquisition, then invalidate or write as needed.
- `nvnode_pager_setsize()` holds the VM object while adjusting object size and pages.
- VM page unmapping loops use `vm_page_lookup_busy_wait()`, `vm_page_protect(VM_PROT_NONE)`, `vm_page_wakeup()`, and `lwkt_yield()` to avoid long monopolization.

## Notable Design Details

- The VM object may remain larger than byte EOF so it covers the full last buffer. Userland faults beyond EOF are prevented by unmapping/protecting pages rather than invalidating the buffer-covered VM pages.
- Zero-filling uses delayed/write-behind semantics to avoid races where a clean buffer could be discarded and reread before the filesystem completes allocation or truncation.
- Dirty range fields are adjusted when zeroing a buffer already marked `B_DELWRI`.
- Both truncation and extension clear `bp->b_bio2.bio_offset` to `NOOFFSET`, forcing remapping for filesystems that avoid overwriting existing physical blocks.

## Cross-File Relationships

- This file is the newer counterpart to `vtruncbuf()` and `vnode_pager_setsize()` paths still present in `vfs_subr.c`.
- Filesystem implementations call these helpers when they adopt the newer VFS/VM coherency contract.
- It depends on the same vnode buffer trees and buffer flags maintained by `bgetvp()`, `brelvp()`, and `reassignbuf()` in `vfs_subr.c`.
- It participates in the same dirty-buffer and write-tracking ecosystem used by `vfs_sync.c`.

## Research Notes

- The key semantic point is buffer-granular VM object coverage with page-granular user visibility enforcement.
- High-risk areas are partial-buffer zeroing, dirty range preservation, concurrent buffer instantiation during VM cleanup, and filesystems passing correct old/new block sizes and block offsets.
