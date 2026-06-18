# sources/sync-backup/git-lfs/t/cmd/lfstest-getnumcpu.go

Purpose: prints Go's detected CPU count for shell tests.

Important API: `main` calls `runtime.NumCPU`.

Control flow: single print with no newline.

State/persistence behavior: none.

Dependencies/integration: allows shell tests to adapt parallelism or expectations to the runtime.

Risks: value reflects Go runtime/container view, not necessarily physical CPUs.

Test signals: stdout integer.
