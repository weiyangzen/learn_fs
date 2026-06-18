# sources/sync-backup/casync/src/caorigin.h

## Purpose
`caorigin.h` declares the origin-provenance container used to describe the source locations for a byte stream. It is primarily useful for reflink-aware decoding and for reporting where returned seed data came from.

## Important APIs, Types, and Functions
`struct CaOrigin` stores `first`, `others`, item counts, allocation count, and total bytes. Public functions cover allocation, unref, flush, append, indexed lookup, concat, void insertion, item/byte advancement, prefix extraction, and dumping. Inline helpers return item and byte counts with `NULL` treated as empty.

## Control Flow
Callers append known-size locations as bytes are produced, then advance or extract prefixes as bytes are consumed by downstream readers.

## State and Persistence
All state is heap owned and references `CaLocation` instances. The header exposes internals, so invariants depend on disciplined callers.

## Dependencies and Integration Points
The header includes `calocation.h` and is consumed by decoder, cache, public sync, and seed APIs.

## Risks
Public structure mutation can break the byte count and merge invariants. Ownership of returned `CaLocation*` from `ca_origin_get()` remains with the origin; callers must ref it if retained.

## Test Signals
`test/test-caorigin.c` directly exercises the declared API.
