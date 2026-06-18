# sources/security-integrity/ecryptfs-utils/src/libecryptfs/decision_graph.c

## Purpose
Generic decision-graph engine used by libecryptfs to turn parsed mount/key-module options into a stack of kernel mount parameters. It can consume pre-supplied name/value pairs, prompt through callbacks, follow transition nodes, and dynamically build linear subgraphs for key modules.

## Important APIs, types, and functions
- Stack helpers `stack_push`, `stack_pop`, and `stack_pop_val` manage `struct val_node` lists containing generated mount options.
- `do_transition`, `alloc_and_get_val`, `eval_param_tree`, and `ecryptfs_eval_decision_graph` form the evaluation loop.
- Graph topology helpers include `add_transition_node_to_param_node`, `ecryptfs_set_exit_param_on_graph`, dump helpers, and parameter insertion helpers.
- `ecryptfs_build_linear_subgraph` creates key-module parameter chains and finalizes them by adding a key to the keyring.

## Control flow
Evaluation starts with verbosity detection from the `verbosity` option. For each node, the engine resolves a value, then `do_transition` checks explicit value matches, option-list matches, and finally the `default` transition. Transition callbacks can push mount options, add keys, mutate next-node pointers, or signal `WRONG_VALUE`/`MOUNT_ERROR`. Linear key-module subgraphs enter with a selected module alias, collect parameter values in order, convert them into `key_mod->param_vals`, call `ecryptfs_add_key_module_key_to_keyring`, and push `ecryptfs_sig=<sig>`.

## State and persistence behavior
The engine mutates `param_node->val`, `nvp` processed flags, transition `next_token` pointers, and the mount-parameter stack. It allocates prompt strings, parameter arrays, and transition nodes. Persistent external state appears only through callbacks, especially keyring insertion from generated key-module subgraphs.

## Dependencies and integration points
Used by `module_mgr.c` to implement mount and key-generation flows. It depends on `decision_graph.h`, `ecryptfs.h`, key-module lookup, and keyring insertion in `key_management.c`. Prompt behavior is supplied by `struct ecryptfs_ctx`.

## Risks and edge cases
Some graph mutations are global static-node mutations, so repeated evaluations must reset enough state to avoid stale transitions or suggested values. `set_exit_param_node_for_arr` uses `sizeof` on a function parameter array, which cannot compute the real array length. `do_transition` keeps static repeat tracking and can be surprising across independent evaluations. Memory ownership is mixed: `stack_pop` frees `val`, but some pushed values are string literals in module manager callbacks.

## Test signals
Tests should construct small synthetic graphs for default transitions, explicit transitions, wrong values, implicit transitions, and prompt callbacks. Integration tests should process mount options with one and multiple keys, confirm generated mount option stack contents, and verify no stale graph state leaks between repeated invocations.
