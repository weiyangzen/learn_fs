# sources/storage-engines/lmdb/libraries/liblmdb/midl.c

## Purpose
`midl.c` implements LMDB's internal ID-list and ID-to-pointer-list utilities used for page number lists, dirty-page tracking, and related internal structures.

## Important APIs, types, and functions
For `MDB_IDL`, it provides `mdb_midl_search`, `mdb_midl_alloc`, `mdb_midl_free`, `mdb_midl_shrink`, `mdb_midl_need`, append helpers, `mdb_midl_xmerge`, and `mdb_midl_sort`. For `MDB_ID2L`, it provides search, insert, append, alloc/free, and grow helpers. When `MDB_RPAGE_CACHE` is enabled, it also provides `MDB_ID3L` search/insert helpers.

## Control flow
The IDL routines maintain arrays whose visible pointer starts after a hidden allocation-length slot. Searches are binary searches over descending IDLs or ascending ID2L/ID3L lists. Appends grow capacity with `realloc` when needed. Sorting uses quicksort with median selection and insertion sort for small ranges. Merge walks from the tails of two descending IDLs and writes a merged descending result in place.

## State and persistence behavior
The file manages heap memory only; it does not persist data directly. Its data structures represent persistent LMDB page IDs while transactions are being built or reconciled, so ordering and capacity correctness affect database file consistency indirectly.

## Dependencies and integration points
`mdb.c` and other internals include `midl.h` for page-list management. The code depends on `lmdb.h` integer typedefs and on the invariant that `ids[0]` is a count while `ids[-1]` is capacity for allocated IDLs.

## Risks and edge cases
The hidden header pointer convention is efficient but fragile: callers must free the shifted pointer with `mdb_midl_free`, not plain `free`. Several helpers assume enough destination capacity. Sorting is descending for `MDB_IDL` while `MDB_ID2L` is ascending, so mixing assumptions can corrupt search results. Return codes use both `ENOMEM` and negative sentinel values depending on type.

## Test signals
Focused tests should cover duplicate insertion rejection, capacity growth and shrink, search insertion points at boundaries, sort order, merge correctness with adjacent page IDs, and allocation failure paths.
