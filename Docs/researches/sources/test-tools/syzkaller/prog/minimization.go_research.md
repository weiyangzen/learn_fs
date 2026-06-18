# sources/test-tools/syzkaller/prog/minimization.go

Purpose: reduces programs while preserving an external equivalence predicate, supporting corpus minimization, crash reproducer minimization, snapshot-mode readability, and calls-only mode.

Important APIs/types/functions: stats variables, `MinimizeMode`, `Minimize`, `removeCalls`, `removeUnrelatedCalls`, `relatedCalls`, `uses`, `resetCallProps`, `minimizeCallProps`, `minimizeArgsCtx.do`, and type-specific `minimize` methods for structs, unions, pointers, arrays, ints/flags/procs, resources, and buffers.

Control flow and state: `Minimize` wraps the predicate with sanitize/debug/dedup/stat accounting, records target call identity, removes calls, optionally resets/minimizes props and args, and restarts per-call traversal after each committed simplification. Call removal tries trailing calls, unrelated resource/file-connected calls, then individual reverse removals. Arg minimization mutates a cloned working program, asks the predicate, commits by replacing `*p0`, and tracks tried paths to avoid duplicates.

Dependencies and integration: depends on `Clone`, `RemoveCall`, `ForeachArg`, resource `uses`, filename buffers, target size assignment, conditional defaulting, hash/stat packages, and serialization for dedup.

Risks: minimization mutates candidate trees in place; stale-tree and shared-program panics guard commit protocol. Modes intentionally skip expensive or readability-focused reductions. Compressed buffers under `no_minimize` calls panic if reached. Resource and condition changes require careful restoration on failed predicates.

Test signals: `minimization_test.go` covers call removal, resource replacement, props retention/removal, pointer/pointee minimization, filename shortening, no-minimize calls, unrelated-call pruning, random duplicate avoidance, and call-index preservation. `expr_test.go` covers conditional interactions.
