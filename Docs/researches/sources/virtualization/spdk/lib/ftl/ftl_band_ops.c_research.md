# File Research: sources/virtualization/spdk/lib/ftl/ftl_band_ops.c

## Purpose
Implements band-level asynchronous IO operations and metadata persistence for opening, closing, freeing, and reading relocation metadata.

## IO Paths
- `ftl_band_rq_write()` writes an internal multi-block relocation/compaction request to the base bdev at the band iterator, advances the iterator, and may mark the band full.
- `ftl_band_rq_read()` reads relocation request entries from the base bdev.
- `ftl_band_basic_rq_write()` and `ftl_band_basic_rq_read()` handle simpler metadata read/write operations, including P2L tail metadata.
- `-ENOMEM` submit failures are queued with SPDK bdev IO wait; other failures abort unless retry mode is enabled.

## Metadata Transitions
- `ftl_band_open()` persists band metadata with state `OPEN`.
- `ftl_band_close()` writes the tail P2L map, computes CRC, persists metadata with state `CLOSED`, and then transitions through the band state machine.
- `ftl_band_free()` persists metadata with state `FREE`, clears close sequence and P2L checksum, then releases P2L resources.
- Tail metadata reads verify P2L CRC before handing a band to GC.

## GC Entry
`ftl_band_get_next_gc()` selects a relocation band, sets owner callbacks, and reads its tail P2L map before invoking the caller.

## Dependencies
Uses SPDK bdev module APIs, FTL request structures, FTL metadata persistence, CRC, and band/core helpers.
