# File Research: sources/virtualization/qemu/block/qcow2-threads.c

Provides threaded helper execution for qcow2 compression, decompression, encryption, and decryption so CPU-heavy data transforms run through QEMU’s thread pool while callers remain coroutine-based.

Key entry points:
- `qcow2_co_process()` limits concurrent qcow2 worker tasks with `s->nb_threads`, waits on `s->thread_task_queue` when `QCOW2_MAX_THREADS` is reached, submits work via `thread_pool_submit_co()`, then wakes the next waiter.
- `qcow2_co_compress()` selects zlib or zstd compression based on `s->compression_type`.
- `qcow2_co_decompress()` selects zlib or zstd decompression based on `s->compression_type`.
- `qcow2_co_encrypt()` and `qcow2_co_decrypt()` run `qcrypto_block_encrypt()` / `qcrypto_block_decrypt()` in the same worker framework.

Compression behavior:
- zlib uses raw deflate/inflate with a negative window size and expects decompression to fill the destination cluster exactly.
- zlib decompression accepts `Z_BUF_ERROR` only when the output buffer is full, because qcow2 compressed sizes are sector-granular rather than exact.
- zstd support is conditional on `CONFIG_ZSTD`.
- zstd compression uses the streaming API but intentionally performs one end call; a nonzero result is treated as destination-too-small or I/O error.
- zstd decompression loops until the output buffer is full, rejects no-progress iterations, and treats unfinished frames after a full output as corruption/error.

Crypto behavior:
- `qcow2_co_encdec()` chooses the crypto IV offset from host offset or guest offset according to `s->crypt_physical_offset`.
- Encryption/decryption require `s->crypto` and assert guest offset, host offset, and length alignment to the crypto sector size.
- Zero-length crypto operations return success without worker submission.

Important invariants:
- Worker concurrency accounting is protected by `s->lock`.
- Compression wrappers pass stack-allocated argument structs only because `thread_pool_submit_co()` waits for completion before returning.
- Compression/decompression return negative errno-style values; successful decompression returns 0, successful compression returns compressed byte count.
- Unsupported compression enum values abort, so callers must validate image compression type earlier.

Filesystem/block relevance:
- This is qcow2’s CPU transform offload layer for compressed clusters and encrypted payloads. It does not manage allocation, but it directly affects how cluster data is encoded before writes and decoded after reads.

Notable risks:
- The thread cap serializes excess CPU work; queue behavior depends on proper wakeup after every completed worker task.
- zstd decompression intentionally guards against infinite loops when the library consumes or produces no data.
- Alignment assertions mean invalid crypto call sites fail hard in debug/assert-enabled builds.
