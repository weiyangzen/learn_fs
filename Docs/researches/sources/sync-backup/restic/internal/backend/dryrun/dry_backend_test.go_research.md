# sources/sync-backup/restic/internal/backend/dryrun/dry_backend_test.go

Purpose: Behavioral tests for the dry-run backend wrapper.

Important APIs and functions: `newBackends` returns dry-run and underlying memory backends. `TestDry` drives a scripted sequence of operations over both backends.

Control flow and state: The test directly saves/removes on the memory backend when it needs real state, then performs dry-run saves/removes/deletes and confirms they do not change that state. It also validates stat/load/list outputs and expected not-found errors.

Dependencies and integration: Uses `mem.New`, `backend.Handle`, `backend.NewByteReader`, sorting for deterministic list comparison, and `IsNotExist` checks.

Risks and test signals: Guards non-mutating dry-run semantics and read delegation. It intentionally avoids the generic backend suite because dry-run writes are not persistent.
