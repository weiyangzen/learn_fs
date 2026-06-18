# File Research: sources/os/linux/linux/fs/netfs/write_collect.c

Collects, assesses, completes, and retries netfs write subrequests.

Key responsibilities:
- Tracks multiple write streams, typically upload-to-server and write-to-cache.
- Advances request collection point to the minimum collected offset across active streams.
- Ends folio writeback only after all required streams have completed the folio range.
- Handles stream failures, partial writes, retries, cache invalidation on cache write failure, and async kiocb completion.
- Releases netfs writeback group refs after folios are written back.

Important exported APIs:
- `netfs_folio_written_back()`.
- `netfs_write_subrequest_terminated()`.

Important internal APIs:
- `netfs_write_collection()`.
- `netfs_write_collection_worker()`.

Important behavior:
- Streaming write metadata is detached once writeback completes.
- `NETFS_FOLIO_COPY_TO_CACHE` folios are treated specially and do not upload to server.
- Server upload failures set mapping errors.
- Cache write failures can invalidate cache via netfs op but do not necessarily fail server writeback.
- Partial successful writes set `NETFS_SREQ_NEED_RETRY`.
- Completion clears `NETFS_RREQ_IN_PROGRESS`, updates `ki_pos`, and completes async `kiocb` if present.
