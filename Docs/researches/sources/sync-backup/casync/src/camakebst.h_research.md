# sources/sync-backup/casync/src/camakebst.h

## Purpose
Declares the binary-search-tree permutation helper used for sorted table serialization.

## Important APIs, Types, and Functions
`ca_make_bst(const void *input, size_t n, size_t size, void *output)` copies `n` fixed-size sorted elements into array-backed BST order.

## Control Flow
No implementation is in the header. Callers provide sorted input and consume permuted output.

## State and Persistence Behavior
No state is declared. The function affects persisted layout only through caller-owned output buffers.

## Dependencies and Integration Points
Includes `<sys/types.h>` for `size_t`. Used by name-table/goodbye construction paths.

## Risks
The contract does not document behavior for `n == 0`, overlapping buffers, or invalid sizes; callers must enforce those preconditions.

## Test Signals
Compile coverage and table-search tests through `camakebst.c` callers are sufficient.
