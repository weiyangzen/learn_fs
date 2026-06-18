# sources/storage-engines/lmdb/libraries/liblmdb/midl.h

## Purpose
`midl.h` declares LMDB's internal ID-list types, size constants, macros, and helper prototypes for managing page-ID collections and ID-to-pointer collections.

## Important APIs, types, and functions
It defines `MDB_ID`, `MDB_IDL`, IDL size limits (`MDB_IDL_DB_SIZE`, `MDB_IDL_UM_SIZE`, and max variants), macros such as `MDB_IDL_SIZEOF`, `MDB_IDL_FIRST`, `MDB_IDL_LAST`, and `mdb_midl_xappend`, plus prototypes for all `mdb_midl_*` helpers. It also defines `MDB_ID2`, `MDB_ID2L`, and optional `MDB_ID3`/`MDB_ID3L` cache structures under `MDB_RPAGE_CACHE`.

## Control flow
The header has no runtime control flow. It codifies layout and ordering contracts: `MDB_IDL` stores a count in element 0 and IDs from 1..count in descending order, while allocated IDLs also keep capacity at `ids[-1]`; `MDB_ID2L` stores count in `ids[0].mid` and sorted items afterward.

## State and persistence behavior
The header defines in-memory state structures. These structures are used by LMDB internals to describe database page IDs and dirty-page mappings during transactions, indirectly protecting persistent page allocation and free-list correctness.

## Dependencies and integration points
It includes `lmdb.h` for `mdb_size_t` and conditional compile flags, and exposes C linkage for C++ consumers. It is not part of the public user API despite depending on public LMDB typedefs.

## Risks and edge cases
Macros directly index shifted pointers and can read or write out of bounds if callers pass unallocated or undersized arrays. The comment notes many legacy macros are unused; changing constants can affect stack usage, heap growth, and maximum freelist sizes. Optional `MDB_ID3` fields are only available when read-page caching is enabled.

## Test signals
Build tests with and without `MDB_RPAGE_CACHE`, unit tests for macro expectations, and integration tests stressing dirty-page and free-list growth validate this header's contracts.
