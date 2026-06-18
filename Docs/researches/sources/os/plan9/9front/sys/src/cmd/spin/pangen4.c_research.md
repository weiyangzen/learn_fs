# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.c

Backward-move and queue-undo code generator support.

Key behavior:
- `undostmnt` emits generated code to reverse Promela statements during DFS backtracking.
- Handles undo for `run` by deleting the newest process, sends by `unsend`, receives by `unrecv` plus restoration of backed-up variables, process deletion by `p_restor`, priority updates by restoring saved priority, assignments by restoring `trpt->bup.oval(s)`, and embedded C by `sv_restor`.
- Skips undo for side-effect-free controls such as goto, break, else, printm, and pure polling receives.
- `any_undo` and `any_oper` decide whether a transition needs a backward case.
- `check_proc` recursively finds nested `run` or process deletion operations that must be undone even inside expressions/assertions/prints.
- `genunio` emits `unsend` and `unrecv` implementations for every queue type, including sorted-send slot compaction, rendezvous unblocking, message shifting, and field restoration.
- `proper_enabler` validates expressions allowed in process `provided` clauses and marks `has_provided`.

Dependencies:
- Uses queue metadata from `qtab`, generated templates `R13`/`R14`/`R15` from `pangen3.h`, and statement/name emission from `pangen2.c`.
- Depends on global generation context: `Pid`, `eventmapnr`, `m_loss`, `multi_oval`, `has_sorted`, and `has_provided`.

Research notes:
- This file is critical for state-space search correctness because all destructive forward moves must be exactly reversible.
- Backup-value ordering must match `pangen2.c` forward generation, especially for random receives and merged transitions with multiple backed-up values.
