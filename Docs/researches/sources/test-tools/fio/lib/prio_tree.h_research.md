# sources/test-tools/fio/lib/prio_tree.h

Purpose: declares priority search tree node/root/iterator structures and inline initialization/query helpers.

Important APIs/types: `struct prio_tree_node` with `start` and inclusive `last`, `struct prio_tree_root`, `struct prio_tree_iter`, initialization macros, `prio_tree_iter_init`, emptiness/root helpers, `prio_tree_entry`, and mutation/iteration prototypes.

Control flow/state: callers embed nodes in their own objects, initialize roots and nodes, set interval bounds before insertion, and use `prio_tree_iter_init` plus repeated `prio_tree_next` for overlap queries.

Dependencies/integration: includes fixed-width integers. The implementation assumes sentinel self-pointers for empty child/root states.

Risks/test signals: callers must initialize nodes and must not alter `start/last` while inserted. Tests should assert iterator correctness for inclusive endpoints.
