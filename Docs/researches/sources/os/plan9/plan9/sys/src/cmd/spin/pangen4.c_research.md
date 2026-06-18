# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.c

This file emits reverse/backtracking code for generated verifier moves and queue undo helpers.

Key behavior:
- `undostmnt()` emits C code to undo a single Promela statement after backtracking.
- Handles undo for `run`, send, receive, assignments, process deletion, embedded C, assertions/prints containing `run`, and process restoration.
- `any_undo()` tells the generator whether a statement needs a reverse case.
- `any_oper()` searches an AST for a specific operator.
- `check_proc()` finds nested `run` or process-deletion operators that require reverse handling.
- `genunio()` emits generated `unsend()`/`unrecv()` queue restoration logic by queue type.
- `proper_enabler()` validates `provided`/enabler expressions and marks `has_provided`.

Important details:
- Receive undo is the most complex path: it restores removed queue fields, restores variables from `trpt->bup.oval` or `trpt->bup.ovals`, handles random receive index `XX`, and skips pure polls without side effects.
- Send undo calls generated `unsend()` and respects lossy-send mode.
- Assignment undo restores saved lvalue values and recursively handles nested process operations on the right-hand side.
- `genunio()` emits per-queue-type field shifting/zeroing logic for sorted send and receive rollback.
- Rendezvous queues require special blocked-state restoration through `boq`, `UnBlock`, and previous move status.
- `proper_enabler()` rejects local or side-effecting constructs that are not valid process `provided` expressions.

Filesystem relevance:
- Indirect. This is verifier backtracking support; no filesystem implementation logic.
