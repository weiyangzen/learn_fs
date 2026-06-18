# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.c

Static FSM analysis pass used before verifier code emission.

Key behavior:
- Builds an internal FSM graph from process `Sequence`/`Element` structures with `ana_seq` and `FSM_EDGE`.
- Tracks per-transition variable reads and writes through `ana_stmnt` and `ana_var`.
- `FSM_ANA` performs dataflow analysis to find local variables that become dead after a read/write along all future paths, then attaches dead-variable reset/backup metadata to the originating element.
- `FSM_MERGER` identifies safe statement merge chains and merge starts, excluding blocking operations, alternatives, escapes, labels, remote-reference states, embedded C, priorities, atomic/d_step boundaries, global effects, and unsafe rendezvous cases.
- Uses `build_step`, `eligible`, and `canfill_in` to mark `Element.merge`, `merge_single`, `merge_start`, and `merge_in`.
- Supports optional AST export with predecessor edges and calls to `AST_store`/`AST_slice`.
- Frees/reuses FSM state, transition, and variable-use nodes through local freelists.
- `spit_recvs` emits an `Is_Recv` table and optional `no_recvs` helper for rendezvous optimization.

Dependencies:
- Consumes global process list `rdy`, all elements `Al_El`, Spin AST node types, label helpers, `has_global`, and statement comment printing.
- Produces metadata later consumed by `pangen2.c` and `pangen4.c`.

Research notes:
- This file is an optimization and analysis layer, not final code emission except for receive helper generation.
- Merge analysis is deliberately conservative; many constructs are excluded to preserve partial-order reduction and backtracking correctness.
