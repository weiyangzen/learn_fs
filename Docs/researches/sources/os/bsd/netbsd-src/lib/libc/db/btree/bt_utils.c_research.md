# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_utils.c

Contains shared btree return and comparison helpers. `__bt_ret` materializes a leaf key/data pair into caller-provided `DBT`s. It returns direct pointers into the pinned page for ordinary records when safe, but copies data when `copy` is requested, `B_DB_LOCK` is enabled, or the key/data lives in overflow pages.

`__bt_cmp` compares a user key against a btree leaf or internal entry. It special-cases the leftmost internal separator as smaller than all user keys, loads overflow keys through `__ovfl_get`, and delegates ordering to the tree's configured `bt_cmp` function.

`__bt_defcmp` is the default bytewise comparator: it compares common-prefix bytes and then sizes. `__bt_defpfx` returns the shortest prefix length needed to distinguish two ordered keys, used by split-time internal-key compression.

Dependencies include `BLEAF`, `BINTERNAL`, `GETBLEAF`, `GETBINTERNAL`, overflow helpers, and `BTREE` flags from `btree.h`.

Risks/invariants: direct return pointers require the referenced page to remain pinned. `__bt_cmp` uses `bt_rdata` as scratch for overflow key material, so callers must not assume that buffer remains stable across later operations.
