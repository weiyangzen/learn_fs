# File Research: sources/os/linux/linux-stable/fs/ocfs2/mmap.c

Purpose: implements OCFS2 mmap fault and page-mkwrite handling, including signal masking around clustered faults, allocation for writable mapped pages, and VMA operation installation.

Read coverage: complete file read, 177 lines.

Major logic:
- `ocfs2_fault()` blocks signals around `filemap_fault()` so cluster lock paths do not abort with restart errors, then traces the fault.
- `__ocfs2_page_mkwrite()` validates that the folio still belongs to the inode mapping, is uptodate, and lies within current `i_size`; otherwise it returns `VM_FAULT_NOPAGE` for VM retry.
- For valid writable faults, it computes full-page or EOF-trimmed length and calls `ocfs2_write_begin_nolock()` / `ocfs2_write_end_nolock()` to allocate and prepare the whole page for mmap writeback.
- `ocfs2_page_mkwrite()` wraps the helper in `sb_start_pagefault()`, signal blocking, exclusive inode cluster lock, and exclusive `ip_alloc_sem`, ensuring remote truncation and local extent mutation cannot race the page becoming writable.
- `ocfs2_mmap_prepare()` refreshes atime under OCFS2 inode locking, installs `ocfs2_file_vm_ops`, and returns success.

Important entry points:
- `ocfs2_mmap_prepare()` is the VFS mmap preparation hook.
- Internal VM operations: `ocfs2_fault()`, `ocfs2_page_mkwrite()`.

Concurrency and lifetime:
- Page-mkwrite takes the inode cluster lock in exclusive mode and `ip_alloc_sem` write side before allocation.
- Signals are blocked in fault paths to avoid `-ERESTARTSYS` escaping cluster lock/message operations.
- The folio is revalidated before allocation because page cache truncation or remote lock downconversion can detach it.

Important dependencies:
- Uses OCFS2 write-begin/write-end no-lock helpers, inode locks, file operations, superblock pagefault accounting, Linux folio/page fault APIs, and tracepoints.

Risk and edge cases:
- The i_size check alone is insufficient because a remote truncate/reextend can reuse the index; the write path must recheck mapping under locks.
- `ocfs2_write_end_nolock()` is expected to return the full requested length; mismatch is treated as a bug.
- `ocfs2_mmap_prepare()` currently returns 0 even if atime locking failed after logging; it still installs VM ops.
