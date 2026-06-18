# sources/sync-backup/casync/src/camakebst.c

## Purpose
Builds an array-backed binary-search-tree permutation from a sorted input array. casync uses this layout for lookup tables such as directory goodbye/name tables so searches can proceed with monotonically increasing array indexes.

## Important APIs, Types, and Functions
The public function is `ca_make_bst(input, n, size, output)`. Static helpers `pow_of_2`, `log_of_2`, and `make_bst_inner` compute the root index and recursively copy left/right subtrees into heap-style positions `2*i+1` and `2*i+2`.

## Control Flow
`ca_make_bst` computes tree height from `log_of_2(n) + 1` and starts recursion at output index 0. `make_bst_inner` chooses a balanced root `k` based on the subtree size and power-of-two thresholds, copies that element, then recurses into the lower and upper sorted ranges.

## State and Persistence Behavior
No persistent state exists. The output permutation is persisted indirectly when callers serialize the resulting table.

## Dependencies and Integration Points
Depends on `util.h` for assertions and `memcpy`. Integrated by name-table/goodbye table generation.

## Risks
`ca_make_bst` assumes `n > 0`; if `n == 0`, `log_of_2(0)` would be invalid. Input must be sorted and output must be large enough for `n` elements. Overlapping input/output is not explicitly handled.

## Test Signals
Test zero handling at caller boundaries, one/two/many elements, odd/even sizes, sorted-search correctness, output bounds under sanitizers, and integration with goodbye table lookup.
