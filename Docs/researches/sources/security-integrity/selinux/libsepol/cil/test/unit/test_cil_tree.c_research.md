# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.c

Purpose: Implements CuTest coverage for basic CIL tree allocation and initialization.

Important APIs and functions: `test_cil_tree_node_init()` validates `cil_tree_node_init`; `test_cil_tree_init()` validates `cil_tree_init`. Both assert null child/parent/data/next fields and zeroed flavor/line state.

Control flow: Each test creates a tree node or tree, inspects initialized fields, asserts expected defaults, then frees the top-level allocation.

State and persistence: State is heap-only and short lived. `test_cil_tree_init` checks the root node attached to the allocated `struct cil_tree`, but only frees `test_tree`; deeper cleanup depends on allocation layout and the broader test process.

Dependencies and integration points: Includes public `policydb.h`, CuTest, the local header, and internal `cil_tree.h`.

Risks: Tests cover only pristine initialization, not child insertion, destruction, traversal, parse data attachment, or allocation failure.

Test signals: Passing null/zero default assertions catch regressions in constructor initialization that would destabilize parser and resolver code.
