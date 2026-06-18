# File Research: sources/os/linux/linux/fs/ocfs2/mmap.c

`mmap.c` implements OCFS2’s clustered mmap fault handling.

Main responsibilities:
- `ocfs2_fault()` wraps `filemap_fault()` while blocking signals, matching OCFS2’s lock/messaging paths that may otherwise return restart-style errors at awkward VM fault points.
- `__ocfs2_page_mkwrite()` prepares a clean page-cache folio for write:
  - Rejects stale/unmapped/not-uptodate/out-of-size folios with retry-style `VM_FAULT_NOPAGE`.
  - Uses `ocfs2_write_begin_nolock()` and `ocfs2_write_end_nolock()` to allocate and prepare the full page or final partial page.
  - Returns `VM_FAULT_LOCKED` when the folio is successfully locked/prepared.
- `ocfs2_page_mkwrite()` is the cluster-aware write-fault wrapper:
  - Starts pagefault accounting.
  - Blocks signals.
  - Takes the inode metadata lock in write mode to block remote truncation and downconvert page truncation.
  - Takes `ip_alloc_sem` in write mode to serialize against file truncation and extent-tree mutation.
  - Releases all locks and ends pagefault accounting.
- Defines `ocfs2_file_vm_ops` with fault and page_mkwrite hooks.
- `ocfs2_mmap_prepare()` takes an atime-aware inode lock once during mmap setup, then installs OCFS2 VM ops.

Key invariants:
- mmap write faults reuse the normal buffered write allocation path rather than duplicating allocation rules.
- Cluster inode locking prevents concurrent remote truncation while a page is made writable.
- Allocation semaphore protects extent tree and file size interactions during page-mkwrite.
