# File Research: sources/local-fs/squashfs-tools/squashfs-tools/caches-queues-lists.c

Implements the shared pthread queue/cache infrastructure used by the mksquashfs pipeline.

Main components:
- `struct queue`: bounded circular queue with `empty`/`full` condition variables.
- `struct seq_queue`: hash-backed sequence queue that lets producer threads finish out of order while consumers retrieve in deterministic order.
- `struct read_queue`: per-reader circular queues merged by earliest file/version/block ordering.
- `struct cache`: lookup-capable or shrinking cache of `file_buffer` objects.
- `struct queue_cache`: combined read queue and write-buffer cache for atomically selecting input buffers and allocating output buffers.

Queue behavior:
- `queue_put()` and `queue_get()` block on full/empty conditions.
- `queue_get_tid()` integrates thread-idle tracking before waiting.
- Flush/dump helpers reset or report queue state.

Sequence queues:
- `main_queue_put/get()` order by `file_count`, `block`, and `version`, updating state according to `NEXT_BLOCK`, `NEXT_FILE`, or `NEXT_VERSION`.
- `order_queue_put/get()` order by monotonic `sequence`.
- Hash tables reduce ordered lookup cost.

Caches:
- `cache_init()` supports grow/shrink policy and freelist-first vs grow-first behavior.
- `cache_lookup()` increments use counts and removes reused entries from the freelist.
- `cache_get()` allocates or reuses blocks, optionally hashing by index.
- `cache_get_nowait()` creates a locked entry or returns `NULL` if no buffer is available.
- `cache_wait_unlock()` and `cache_unlock()` coordinate consumers waiting for another thread to fill a locked buffer.
- `cache_block_put()` decrements references and either freelists or frees the buffer.

Combined queue/cache:
- `queue_cache_set()` creates per-thread read queues and write-cache pools.
- `queue_cache_get_tid()` chooses the earliest readable buffer from a thread that also has write-buffer capacity, then returns both read and write buffers together.
- `queue_cache_hash()`, lookup, put, flush, and dump mirror the generic cache semantics.

Safety checks:
- Queue and buffer allocation sizes use external `add_overflow()` and `multiply_overflow()` checks.
- Internal impossible states use `BAD_ERROR()`.

Notable quirks:
- Most data structures are never destroyed; they are process-lifetime pipeline infrastructure.
- Correctness relies on callers respecting buffer type and reference-count protocols.
