# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_strategy.c

## Purpose
Implements HAMMER2 logical file buffer strategy I/O. This layer backs the logical buffer cache and handles asynchronous reads/writes, decompression, compression, zero-block conversion, check-code generation, and live dedup heuristics.

## Read Path
`hammer2_vop_strategy()` dispatches `BUF_CMD_READ` to `hammer2_strategy_read()` and writes to `hammer2_strategy_write()`. Reads allocate an XOP, record the logical base offset and bio, and start `hammer2_strategy_read_desc`.

`hammer2_xop_strategy_read()` runs per cluster node. It resolves the inode chain, looks up the data chain at `lbase`, feeds the XOP cluster, then races to complete the frontend once quorum/focus can be collected. Missing data (`ENOENT`) is treated as a sparse zero block. Successful data calls `hammer2_strategy_read_completion()`.

`hammer2_strategy_read_completion()` handles embedded inode data and external data. For external data it records live dedup information if possible, marks the chain releasable, then copies or decompresses based on `bref.methods`: LZ4, ZLIB, or none. LZ4 data is prefixed with an `int` compressed size.

## Write Path
`hammer2_strategy_write()` marks the inode dirty, increments logical-write-in-progress hysteresis, starts a buffer-cache transaction, creates a modifying strategy XOP, and waits if the write pipe exceeds `hammer2_flush_pipe`.

`hammer2_xop_strategy_write()` copies the logical buffer to per-thread scratch before releasing the frontend bio lock, resolves the parent chain, calls `hammer2_write_file_core()`, feeds the XOP result, and completes the bio when collection reaches completion/quorum.

`hammer2_write_file_core()` selects among:
- no compression: assign physical storage, write direct/embedded/dedup data;
- `AUTOZERO`: convert all-zero blocks into holes when checks are enabled;
- LZ4/ZLIB/default: zero-check first, then attempt compression.

`hammer2_compress_and_write()` attempts compression when the inode heuristic allows it or `hammer2_always_compress` is set. It requires compression to fit in half the physical block, rounds compressed allocation to 1K-32K, zero-fills the remainder for dedup comparability, assigns physical storage, sets methods/checks, writes data, and records dedup candidates.

`zero_write()` deletes an existing data chain for all-zero writes, or zeroes embedded direct data. `hammer2_write_bp()` writes uncompressed data into a device buffer and sets check codes before issuing sync/async/delayed write.

## Dedup
`hammer2_dedup_record()` stores recent data offsets keyed by XXH64/check-derived CRC into a four-way heuristic table and marks DIO dedup-valid bits after data population. `hammer2_dedup_lookup()` validates candidate offsets by radix, DIO allocation/valid masks, and full `bcmp()` before returning a reused physical offset and setting `*datap = NULL`. `hammer2_dedup_clear()` clears heuristic offsets.

## Risk Notes
The code is heavily asynchronous: frontend bio ownership is protected by `xop->lock` and `xop->finished`. Dedup is explicitly heuristic and allows SMP collisions but validates before reuse. Check-code disabled data cannot be deduped because in-place overwrite would make reused storage unsafe.
