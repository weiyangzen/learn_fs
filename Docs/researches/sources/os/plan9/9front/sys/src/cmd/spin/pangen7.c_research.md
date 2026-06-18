# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.c

## Purpose

`pangen7.c` builds a synchronous product automaton when a model has multiple never claims. It reads each claim's control-flow graph, records possible transitions in per-claim matrices, constructs product states as tuples of claim states, prunes dead product transitions, manages accepting/end labels, and prints a generated `never Product` automaton.

This is a generator-time transformation over Spin's parsed Promela/never-claim representation.

## Main Data Structures

- `Succ_List` links product-state successors.
- `OneState` stores a product-state tuple (`combo`) and successor list.
- `SQueue` wraps `OneState` for work queues: `sq` for newly found states, `sd` for done states, `render` for states selected for printing/exploration, and `holding` for already rendered states.
- `State_Stack` detects recursive loops while rendering state bodies.
- `Guard` accumulates transition guard expressions from component claims.
- `matrix[n][from][to]` maps claim `n` transitions from one state number to another to the source `Element`.
- `reached[n][state]` records claim states reached in input/product processing; bit 2 marks states reached in the printable product.
- `Selfs[n]` records synthetic accepting self-loop states inserted at claim termination.

## Input Claim Processing

`sync_product()` is the entry point. It returns immediately if there is only one claim. For multiple claims it allocates `Ist`, `Nacc`, `Nst`, `reached`, `Selfs`, and the four-dimensional transition matrix. It clears `DONE` on all elements, finds initial states for each claim, records whether each claim has accept labels, and calls `get_seq()` on each claim sequence.

`get_seq()` walks a `Sequence` completely, records transitions with `t_record()`, descends into `if`/`do` options, rejects `unless`, and handles nested `atomic`, `d_step`, and `non_atomic` blocks through `get_sub()`. Atomic and d_step inside never claim products are fatal. It rewrites `else` options into explicit condition nodes representing the negation of other condition options where possible, allowing product construction to reason about them as ordinary guards.

`set_el()` resolves transition targets for end markers, gotos, sequential next elements, and terminal transitions. A terminal `@` is converted to a `true` self-loop and made accepting through `mk_accepting()`.

## Product Construction

`gen_product()` creates the initial tuple state, repeatedly processes newly discovered states from `sq`, moves them to `sd`, and calls `all_successors()`. `all_successors()` recursively enumerates the cross-product of enabled component transitions using `nxt_trans()`, filling `Nst` and invoking `create_transition()` for each full tuple.

`create_transition()` rejects product transitions where any component condition is explicitly false, otherwise it appends the successor to the current product state's list. `find_state()` interns tuple states across `sq`, `sd`, and `render`; `retrieve_state()` removes a state from `sd`.

`prune_dead()` repeatedly removes successors that lead to states with no successors. After initial pruning, `explore_product()` renders without printing to discover which added accepting self-loops are actually reachable. `prune_accept()` removes unreachable synthetic accept labels and recomputes per-claim accept status.

## Rendering

`print_product()` prints `never Product` on the first unfolding, then prints one section per claim unfolding. The unfolding mechanism ensures only accept states from claim 0 in copy 0 are true accept states, while accept transitions in other claims advance to the next copy.

`render_state()` prints labels for accept/end product states via `check_special()`, emits a product state name (`P_state_state..._Uunfolding`), opens a `do`, delegates options to `state_body()`, and closes with `od`. If no state emits options for an unfolding, it prints `0;`.

`state_body()` walks successor transitions and accumulates non-trivial guards from component claim transitions. Component transitions that represent structural `if`/`do`/`non_atomic` movement are followed recursively, effectively pulling their target state forward into the rendered transition. `push_dsts()`/`pop_dsts()` prevent recursion loops; self-loops are recognized and optionally commented.

`complete_transition()` prints a Promela option of the form `:: guard && guard -> goto P..._U...`, omitting literal `true` guards and substituting `true` if all guards are trivial.

## Label Handling

`claim_has_accept()` scans `labtab` for accept labels belonging to a claim. `mk_accepting()` adds an `accept00` label to a synthetic self-loop and sets global `has_accept`. `elim_lab()` removes a label tied to an unreachable synthetic self-loop. `check_special()` detects `end` and `accept` labels for each tuple, supports non-strict pseudo-acceptance for claims with no accept states when other claims do have accept states, and names product accept labels using claim names or `N<n>` for generated names containing colons.

## Notable Risks and Behaviors

- Multiple claims are treated as synchronously advancing component automata; every product transition combines one transition from each claim.
- `else` rewriting assumes claim option guards are conditions; combining `else` with non-condition options is fatal.
- Atomic, d_step, and unless constructs in never claim products are explicitly disallowed.
- Several functions mutate parsed elements and labels in place, including converting terminal `@` to a true self-loop and replacing `else` with a condition.
- Output is printed directly to stdout as Promela source.
