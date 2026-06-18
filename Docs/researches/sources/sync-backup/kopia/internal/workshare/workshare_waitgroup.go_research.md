<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_waitgroup.go -->
# sources/sync-backup/kopia/internal/workshare/workshare_waitgroup.go

- Purpose: Provides `AsyncGroup`, a low-allocation coordination wrapper for workshare pool tasks.
- Important APIs/types/functions: `AsyncGroup`, `Wait`, `Close`, `RunAsync`, `CanShareWork`.
- Control flow: `CanShareWork` reserves pool capacity by sending a semaphore token, and callers must then call `RunAsync` once to send the work item. `Wait` waits once and returns request objects; `Close` ensures waiting happened.
- State and persistence: In-memory wait group pointer, request slice, and lifecycle flags.
- Dependencies and integration points: Works with `Pool` and `ProcessFunc`.
- Risks and edge cases: API has strict usage contracts: double wait, wait after close, use after pool close, or failing to run after capacity reservation can panic or leak capacity.
- Test signals: `workshare_test.go` covers normal recursion and invalid usage panics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_waitgroup.go -->
