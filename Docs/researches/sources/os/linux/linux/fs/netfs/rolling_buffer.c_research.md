# File Research: sources/os/linux/linux/fs/netfs/rolling_buffer.c

Implements rolling folio-queue buffers used by netfs read/write issue and collection paths.

Important exported APIs:
- `netfs_folioq_alloc()`.
- `netfs_folioq_free()`.

Important internal APIs:
- `rolling_buffer_init()`.
- `rolling_buffer_make_space()`.
- `rolling_buffer_load_from_ra()`.
- `rolling_buffer_append()`.
- `rolling_buffer_delete_spent()`.
- `rolling_buffer_clear()`.

Important behavior:
- Rolling buffer starts with an empty queue so producer and consumer pointers can move independently.
- `rolling_buffer_make_space()` allocates a new queue when the head is full and publishes `next` with release semantics.
- Readahead folios are loaded into queue slots and added to a put batch.
- Appended folios may be marked for later put/release decisions.
- Consumer deletes spent queues but keeps the final placeholder queue.
- Clear releases marked folios through a folio batch.

Role:
- Provides the moving backing storage for `ITER_FOLIOQ` request iterators and collector cleanup.
