# File Research: sources/os/linux/linux-stable/fs/netfs/write_collect.c

Collects write subrequest results across parallel write streams.

Key behavior:
- Supports multiple streams, primarily server upload and local cache write.
- Advances each stream independently but advances request `collected_to` only to the minimum collected position across active streams.
- Unlocks/writeback-completes folios once all required streams have covered them.
- Handles streaming-write metadata, dirty group references, and copy-to-cache markers.
- Cache write failure can invalidate the cache without failing server writeback unless the filesystem policy says otherwise.
- Server upload failure records mapping errors.
- Short writes set retry-needed; permanent failures cancel affected stream progress.
- Completion updates kiocb position/completion for async write origins and clears subrequests.
- Termination callback records transferred bytes or errors, sets retry/failure flags, pauses request generation, and wakes collector.

Debug support:
- `netfs_dump_request()` prints request, stream, and subrequest state when writeback unlock finds impossible buffer state.
