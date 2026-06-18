# File Research: sources/virtualization/spdk/lib/ftl/ftl_io.h

## Purpose
Defines FTL user IO, internal relocation request, basic metadata request, IO channel, and helper APIs.

## Key Types
- `struct ftl_io_channel`: device pointer, channel list entry, map pool, poller, submission ring, completion ring.
- `struct ftl_io`: user IO descriptor with LBA, physical address, iovec cursor, metadata, status, request count, callback, flags, type, trace ID, queue entry, NV-cache chunk, L2P pin context, mapping array, and bdev wait entry.
- `struct ftl_rq_entry`: one block of an internal relocation/compaction request with payload, metadata, address, LBA, sequence ID, owner, band IO info, L2P pin context, and bdev IO info.
- `struct ftl_rq`: variable-length internal request with owner callbacks, iterator state, IO state, and entries.
- `struct ftl_basic_rq`: simpler metadata IO request for P2L map and related reads/writes.

## Helpers
Defines request-entry loop macros, basic request initialization/owner setters, `ftl_rq_from_entry()`, and `ftl_io_done()`.

## Dependencies
Includes SPDK stdinc/NVMe/ftl/bdev/util and FTL internal/trace/L2P/metadata headers.
