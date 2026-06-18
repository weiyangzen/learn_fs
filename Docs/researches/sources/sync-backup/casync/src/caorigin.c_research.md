# sources/sync-backup/casync/src/caorigin.c

## Purpose
`caorigin.c` tracks where a stream of bytes came from as a sequence of `CaLocation` objects. This is used by casync decode/cache paths to preserve provenance for reflinks and to describe sparse or void ranges.

## Important APIs, Types, and Functions
`ca_origin_new()`, `ca_origin_unref()`, and `ca_origin_flush()` manage the container. `ca_origin_put()` appends a `CaLocation`, merging with the previous location when `ca_location_merge()` allows it. `ca_origin_concat()` appends a full or byte-limited copy of another origin, including self-concat handling. `ca_origin_advance_items()` and `ca_origin_advance_bytes()` drop consumed leading provenance. `ca_origin_put_void()` appends or extends void ranges. `ca_origin_extract_bytes()` copies a prefix into a new origin. `ca_origin_dump()` prints formatted locations.

## Control Flow
The structure optimizes the first location separately from the `others` array. Appending first fills `first`; later appends attempt to merge into `first` or the last `others` item. Byte advancement first drops whole locations, then advances the first remaining location by patching its offset and size. Concatenation optionally snapshots self-references to avoid mutation while iterating.

## State and Persistence
State is in-memory only: strong references to `CaLocation` objects, count, capacity, and total byte count. Persistence occurs only through formatted `CaLocation` strings when dumped or stored elsewhere.

## Dependencies and Integration Points
The module depends on `calocation.h`. `cadecoder.h`, `casync.h`, `cacache.h`, and `caseed.h` include origin support, and `caseed.c` can return an origin for a served seed chunk.

## Risks
`ca_origin_advance_items()` assumes `origin->first` and sizes are valid and uses `assert(origin->n_bytes > drop_bytes)`, so corrupted state can abort. `ca_origin_concat()` returns `n > 0` even when a byte-limited concat consumed fewer items, so callers should not interpret positive values too specifically. The API rejects unknown-size locations in `ca_origin_put()`, while `ca_origin_put_void()` constructs known-size voids.

## Test Signals
`test/test-caorigin.c` covers append/merge behavior, byte advancement, self-concat, concat from another origin, and byte-limited concat. More edge tests should include exact-boundary advances, over-advances, void extension, and extraction.
