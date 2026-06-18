# sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_unix.go

Purpose: Unix-specific mmap helper for disk committed-content index cache.

Important APIs/types/functions: `(*diskCommittedContentIndexCache).mmapFile` opens a file, maps it read-only with `mmap.Map`, closes the file descriptor immediately, and returns the mapping plus an unmap closer.

Control flow: on open or mmap error, it wraps and returns the error while closing the file on mmap failure. After successful mmap, it closes the file descriptor because Unix mappings remain valid after close. If close fails, it still returns the mapping and a closer that unmaps then returns the close error.

State and persistence behavior: no new persistent state; it maps existing `.sndx` files into memory and releases file descriptors early.

Dependencies/integration: build-tagged for non-Windows. Used by `diskCommittedContentIndexCache.openIndex`.

Risks and edge cases: close errors are deferred until index close. Correct early FD close is important for repositories with many cached indexes.

Test signals: Linux FD growth test opens 200 indexes and verifies descriptor count does not grow proportionally.
