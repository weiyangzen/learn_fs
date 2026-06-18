# File Research: sources/os/linux/linux/mm/fadvise.c

## Purpose

Implements generic POSIX file access advice handling and the fadvise syscalls. It adjusts readahead behavior, marks no-reuse mode, triggers readahead for `WILLNEED`, and flushes/invalidates page cache for `DONTNEED`.

## Main Entry Points

- `generic_fadvise(file, offset, len, advice)`: default advice implementation.
- `vfs_fadvise(file, offset, len, advice)`: dispatches to `file->f_op->fadvise` if present, otherwise generic.
- `ksys_fadvise64_64(fd, offset, len, advice)`: fd-based kernel syscall helper.
- Syscall wrappers:
  - `fadvise64_64`
  - optional `fadvise64`
  - optional compat `fadvise64_64`

## Advice Handling

- `POSIX_FADV_NORMAL`: restores default readahead pages and clears `FMODE_RANDOM | FMODE_NOREUSE`.
- `POSIX_FADV_RANDOM`: sets `FMODE_RANDOM`.
- `POSIX_FADV_SEQUENTIAL`: doubles default readahead and clears random mode.
- `POSIX_FADV_WILLNEED`: computes page range and calls `force_page_cache_readahead()`.
- `POSIX_FADV_NOREUSE`: sets `FMODE_NOREUSE`.
- `POSIX_FADV_DONTNEED`: flushes dirty cache in range, then invalidates full pages only.

## Range Semantics

- Negative `offset` or `len` returns `-EINVAL`.
- `len == 0` means through end of file/address space.
- Overflow in `offset + len` is handled with unsigned math and maps to `LLONG_MAX`.
- `DONTNEED` preserves partial first and last pages to avoid discarding potentially useful data.

## DAX / Noop BDI Behavior

For DAX inodes or `noop_backing_dev_info`, recognized advice values are accepted but ignored. Unknown advice still returns `-EINVAL`.

## Cache Invalidation Details

For `POSIX_FADV_DONTNEED`:

1. `filemap_flush_range()` starts writeback for the requested range.
2. Full-page start/end page indexes are computed.
3. `lru_add_drain()` flushes local LRU additions before invalidation.
4. `mapping_try_invalidate()` attempts invalidation and reports failures.
5. If failures occur, `lru_add_drain_all()` drains remote CPUs and `invalidate_mapping_pages()` retries.

## Locking

Updates to `file->f_mode` are protected by `file->f_lock`.
