# sources/sync-backup/casync/test/test-camakebst.c

Purpose: verifies construction of array layouts suitable for binary-search-tree access.

Important APIs/types/functions: `find_bst` searches the generated layout, `test_makebst_size` builds arrays for sizes and checks ordering/search invariants, and `main` runs sizes across a range.

Control flow/state: allocates local arrays, calls `ca_make_bst`, then asserts each expected value is findable and out-of-range values are absent.

Dependencies/integration: covers `camakebst`, which is used for efficient sorted table layouts.

Risks/test signals: catches off-by-one and tree-shape regressions across small and medium sizes. It does not benchmark lookup performance.

Source research group: `subset-b-009122`.
