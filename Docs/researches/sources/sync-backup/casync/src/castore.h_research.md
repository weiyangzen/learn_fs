# sources/sync-backup/casync/src/castore.h

## Purpose
`castore.h` declares the chunk store API used to persist and retrieve casync chunk files.

## Important APIs, Types, and Functions
It declares opaque `CaStore` and `CaStoreIterator`. Public functions cover normal/cache construction, unref, path setup, compression setup, chunk get/has/put, request statistics, digest selection, iterator construction/unref, and iterator next.

## Control Flow
Callers configure a store path and compression policy, then use get/has/put. Iterators produce root fd, subdir name/fd, and chunk filename tuples until they return `0`.

## State and Persistence
Implementation state is opaque. Stores may persist data under configured roots or remove temporary cache roots when unreferenced.

## Dependencies and Integration Points
The header includes `cachunk.h`, `cachunkid.h`, and `cautil.h`. It is included by public sync and garbage-collection code.

## Risks
Returned chunk data from `ca_store_get()` is implementation-owned. Iterator outputs are only valid until the next iterator advancement or close.

## Test Signals
End-to-end encode/decode tests cover basic store operation. Direct iterator and compression policy tests would improve confidence.
