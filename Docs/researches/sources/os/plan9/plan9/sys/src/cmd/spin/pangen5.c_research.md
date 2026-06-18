# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.c

This file performs static FSM analysis before code generation. It builds per-proctype FSM graphs, computes read/write use information, detects dead local variables, finds safe transition merges, supports AST export, and emits rendezvous-receive metadata.

Key behavior:
- Builds `FSM_state`/`FSM_trans` graphs from `Sequence` and `Element` structures via `ana_seq()` and `FSM_EDGE()`.
- `ana_stmnt()` and `ana_var()` collect read/write uses of variables on each transition.
- `FSM_ANA()` performs dataflow analysis to find local variables that are dead after reads/writes and attaches them to `Element.dead` for generated zeroing/backtracking.
- `FSM_MERGER()` identifies safe nonblocking transitions that can be merged into one generated verifier step.
- `eligible()` and `canfill_in()` screen merge candidates against blocking statements, labels, escapes, remote references, globals, C code, and compound constructs.
- `ana_src()` runs analysis for every process, optionally performs dataflow and merge passes, exports AST/FSM data, and reports unreachable code when verbose.
- `spit_recvs()` emits an `Is_Recv[]` table and optional `no_recvs()` helper for synchronous rendezvous optimization.

Important details:
- FSM state objects, transition objects, and use records are recycled through freelists.
- Dead-variable analysis skips globals, channels, structs, and cases where restoring/zeroing cannot be safely represented.
- Merge analysis distinguishes full merge chains from single eligible follow-on steps and marks `merge`, `merge_start`, `merge_single`, and `merge_in` on elements.
- Blocking operations (`c`, `r`, `s`) are treated conservatively; rendezvous sends are excluded from some merge starts because they can lose atomicity.
- AST export hands retained FSMs to `pangen6.c` via `AST_store()` and then invokes `AST_slice()`.
- The receive table is only emitted for synchronous rendezvous configurations and can conservatively mark `d_step` bodies that begin with receive-like behavior.

Filesystem relevance:
- Indirect. This is compiler analysis for generated verifier quality and state-space reduction.
