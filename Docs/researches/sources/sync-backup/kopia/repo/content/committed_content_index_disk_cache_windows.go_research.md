# sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache_windows.go

Purpose: Windows-specific mmap helper for disk committed-content index cache.

Important APIs/types/functions: `(*diskCommittedContentIndexCache).mmapFile` opens the index file with retries, maps it read-only, and returns a closer that unmaps and then closes the file.

Control flow: it retries `os.Open` up to eight times with exponential backoff from 10 ms to about 1.28 s, logging retry attempts. After successful open, mmap failure closes the file. Unlike Unix, the file descriptor stays open until unmap because Windows requires it.

State and persistence behavior: no new persistent state; it holds an open file handle for the life of the mmap.

Dependencies/integration: build-tagged for Windows. Used by `diskCommittedContentIndexCache.openIndex` and content cache loading.

Risks and edge cases: keeping handles open can affect file deletion/expiry behavior on Windows. Retry logic protects against a rare just-written file open race.

Test signals: not covered by the Linux FD test; Windows-specific tests should exercise open retry and close/unmap ordering.
