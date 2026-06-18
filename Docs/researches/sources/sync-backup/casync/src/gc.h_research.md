# sources/sync-backup/casync/src/gc.h

## Purpose

`gc.h` declares the chunk collection and store cleanup API for casync garbage collection.

## Important APIs, Types, and Functions

It forward-declares `CaChunkCollection`, declares creation/unref helpers, an inline cleanup helper, index ingestion, usage/size getters, flags `CA_GC_VERBOSE` and `CA_GC_DRY_RUN`, and `ca_gc_cleanup_unused(CaStore *store, CaChunkCollection *coll, unsigned flags)`.

## Control Flow

Callers build a collection from indexes and then pass it with a store to cleanup, optionally in dry-run or verbose mode.

## State and Persistence Behavior

The collection owns duplicated chunk IDs. Cleanup can mutate the store unless dry-run is passed.

## Dependencies and Integration Points

It includes `cachunk.h` and `castore.h`, binding GC to chunk ID and store abstractions while hiding the set implementation.

## Risks and Edge Cases

The cleanup helper does not null-check the pointer-to-pointer argument before dereferencing. Callers must observe ownership and dry-run semantics carefully.

## Test Signals

Header-level tests should compile cleanup macro use and flag combinations, and integration tests should validate collection lifecycle with store cleanup.
