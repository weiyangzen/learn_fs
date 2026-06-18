# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen7.c

This file builds the synchronous product of multiple never claims. It is used when the model contains more than one claim and Spin needs a single product never claim named `Product`.

Core data structures:
- `OneState`: one product-state vector, `combo`, plus successor list.
- `SQueue`: queue/list wrapper for product states.
- `Succ_List`: links immediate successor product states.
- `State_Stack`: recursion stack for rendering and loop detection.
- `Guard`: accumulated transition guard list while collapsing intermediate states.

The product construction starts in `sync_product()`. It allocates per-claim state matrices, tracks initial states (`Ist`), accept-state counts (`Nacc`), reachable states, self-loop states, and an `Element ****matrix` indexed by claim/from/to. It then scans all never-claim sequences with `get_seq()` and records transitions with `t_record()`.

Important behavior:
- `get_seq()` rejects `unless`, `atomic`, and `d_step` constructs inside product claims where they cannot be handled.
- `set_el()` converts terminal `@` nodes into true self-loops and marks them accepting through `mk_accepting()`.
- `IF`/`DO` suboptions are converted into explicit matrix transitions; `else` guards are rewritten into negated disjunctions of earlier guards.
- `gen_product()` enumerates the Cartesian successor relation across all claims, prunes dead-end transitions, explores reachable product states, prunes unreachable synthetic accept labels, then prints one unfolded copy per claim.
- `check_special()` emits `accept` and `end` labels and handles pseudo-acceptance for claims without accept labels unless strict mode is enabled.
- `state_body()` recursively skips structural/non-atomic states and emits guarded Promela transitions through `complete_transition()`.

Output shape:
- On first unfolding it prints `never Product {`.
- Each unfolding section is labeled with `/* ============= U%d ============= */`.
- Product states are named `P_<state0>_<state1>..._U<unfolding>`.

Risk notes:
- `retrieve_state()` appears to assign `sd = nq` when removing the head instead of `sd = nq->nxt`; this is old source and may depend on surrounding assumptions, but it is a suspicious removal pattern.
- The algorithm uses global mutable state heavily (`sq`, `sd`, `render`, `holding`, `dsts`, `unfolding`, `not_printing`), so it is tightly coupled to single-threaded code generation.
