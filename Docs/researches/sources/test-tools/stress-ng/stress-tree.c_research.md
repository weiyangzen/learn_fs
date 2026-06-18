# sources/test-tools/stress-ng/stress-tree.c

## Purpose
Implements the `tree` stressor, a CPU/cache/memory/search workload that builds, searches, and tears down several tree structures over randomized 32-bit values. It covers local binary, AVL, B-tree, and treap implementations, plus BSD red-black and splay trees when available.

## Important APIs, Types, And Functions
`stress_tree_metrics_t` accumulates insert, find, remove durations and node counts per method. `stress_tree_method_info_t` maps method names to functions. Node types include `binary_t`, `avl_t`, `btree_t` plus `btree_value_t`, optional `rb_t`, optional `splay_t`, and `treap_t`, all covered by `union tree_node` for a shared allocation. `stress_rndu32()` is a fast deterministic generator for repeatable insert data. Method functions such as `stress_tree_binary()`, `stress_tree_avl()`, `stress_tree_btree()`, `stress_tree_treap()`, `stress_tree_rb()`, and `stress_tree_splay()` implement insert/find/remove cycles. `stress_tree_all()` runs every method except the `all` dispatcher.

## Control Flow
The entry point catches illegal instructions, resets metrics, resolves `tree-method` and `tree-size`, allocates a node array sized as `union tree_node`, and optionally installs a `SIGALRM` longjmp handler to escape long tree operations at timeout. After synchronization it repeatedly invokes the selected method while `rc` remains success and the stressor continues. Each method initializes nodes with the same random sequence, measures insertion, performs a mandatory forward find pass, optionally performs reverse and random find passes under verify mode, removes or resets the tree, updates metrics, and returns. On exit the stressor restores the alarm handler, emits per-method operations/sec metrics, computes a debug geometric mean across methods with data, frees nodes, and returns status.

## State And Persistence Behavior
All data is transient heap memory except B-tree internal nodes, which are allocated and freed per B-tree cycle. Optional BSD tree roots and metrics arrays are static process-local state. No files or kernel objects persist.

## Dependencies And Integration Points
Optional RB and splay support depends on `sys/tree.h` or `bsd/sys/tree.h`. The file uses stress-ng option parsing, target clone annotations, signal wrappers, timing, metrics, and sync helpers. It registers as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH` with `VERIFY_OPTIONAL`.

## Risks And Test Signals
Large `tree-size` values can allocate substantial memory and produce long operations, making the SIGALRM longjmp path important. Duplicate random values may reduce inserted node counts in some structures, but find checks search the original values according to each implementation's semantics. AVL balance-factor updates are subtle and covered by mandatory find checks. Test signals are method-specific metrics, optional verify failures naming the missing node, no B-tree allocation leaks, successful alarm interruption cleanup, and no-resource skip on node allocation failure.
