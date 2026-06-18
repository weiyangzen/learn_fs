# File Research: sources/windows/dokany/dokan_fuse/include/fusemain.h

Private C++ bridge declarations mapping FUSE operations to Dokan callbacks.

Key contents:
- Includes Dokan public API, FUSE API, and utility helpers.
- Defines `CHECKED` and `MAX_READ_SIZE`.
- Declares:
  - `impl_file_locks`: global map of open path lock state guarded by `CRITICAL_SECTION`.
  - `impl_chain_link` and `impl_chain_guard`: per-thread call context stack for `fuse_get_context`.
  - `win_error`: errno-to-NTSTATUS wrapper.
  - `impl_fuse_context`: main adapter object holding FUSE ops, connection info, masks, names, max read, and lock manager.
  - `impl_file_lock`: per-path open-handle and byte-range lock coordinator.
  - `impl_file_handle`: per-open state with flags, FUSE file handle, share mode, and locks.
- `impl_fuse_context` declares adapters for nearly every Dokan operation: create/open, directory enumeration, cleanup, close, read/write, flush, metadata, delete, move, locks, truncation, times, volume, mounted/unmounted.

Role:
- Defines the in-memory model for Dokan FUSE: stateful open handles, context propagation, and callback translation.
