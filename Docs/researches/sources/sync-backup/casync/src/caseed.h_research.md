# sources/sync-backup/casync/src/caseed.h

## Purpose
`caseed.h` declares the opaque seed API for indexing local data and serving chunks or hardlink targets from that seed.

## Important APIs, Types, and Functions
The status enum exposes `CA_SEED_READY`, `CA_SEED_STEP`, `CA_SEED_NEXT_FILE`, and `CA_SEED_DONE_FILE`. Public functions configure base/cache fd or path, step indexing, get or test chunks, get hardlink targets, inspect current path/mode during indexing, set feature flags and chunk sizes, enable hardlink/chunk caching, retrieve a `CaFileRoot`, and read request/time statistics.

## Control Flow
Callers configure the seed, step until ready while optionally displaying current file progress, then use `ca_seed_get()` or `ca_seed_has()` to satisfy chunk requests.

## State and Persistence
The object is opaque. Implementation state includes a cache directory, encoder state, chunk buffers, and request counters. Returned chunk data is owned by the seed object.

## Dependencies and Integration Points
The header includes chunk ID and origin types. It integrates with higher-level sync extraction and cache code.

## Risks
Consumers must handle `-EUNATCH`, `-ENOMEDIUM`, `-ESTALE`, and ownership of optional returned origins. The API does not advertise thread safety; implementation is stateful and single-consumer.

## Test Signals
Covered through end-to-end seed extraction scripts. Unit coverage would be valuable for status transitions and error codes.
