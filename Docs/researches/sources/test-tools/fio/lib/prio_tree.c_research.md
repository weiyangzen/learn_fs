# sources/test-tools/fio/lib/prio_tree.c

Purpose: radix priority search tree for storing intervals and enumerating overlaps in `O(log n + m)` style.

Important APIs/functions: `prio_tree_replace`, `prio_tree_insert`, `prio_tree_remove`, and `prio_tree_next`. Static helpers expand root index width, navigate left/right/parent during overlap iteration, and compare interval overlap.

Control flow: insertion expands the tree when the new interval's heap index exceeds current capacity, swaps nodes to maintain priority by highest `last`, and branches by radix index then interval size. Removal replaces the removed node with a descendant preserving heap priority. Iteration initializes on first `prio_tree_next`, performs pre-order traversal, prunes branches whose heap/radix ranges cannot overlap, and returns matching nodes.

State/persistence: mutates caller-embedded `prio_tree_node` links and root index bits. No allocation or locking.

Dependencies/integration: derived from Linux priority tree code, uses `compiler.h` init attribute to fill `index_bits_to_maxindex`. Suitable for interval overlap queries such as file/page ranges.

Risks/test signals: tree invariants are complex, especially expansion and removal. Tests should cover duplicate intervals, nested/overlapping/non-overlapping intervals, removal of root/internal/leaf nodes, and full traversal after mutations.
