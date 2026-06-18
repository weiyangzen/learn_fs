# sources/sync-backup/git-lfs/t/cmd/lfstest-nanomtime.go

Purpose: prints a file modification timestamp with nanosecond precision.

Important API: `main`.

Control flow: requires one path arg, stats it, then prints `<unix>.<nanoseconds padded to 9 digits>`.

State/persistence behavior: read-only filesystem stat.

Dependencies/integration: used by shell tests that need precise mtime comparisons across platforms.

Risks: filesystem timestamp resolution may be lower than nanoseconds despite Go's representation.

Test signals: stdout timestamp or distinct exit codes for usage/stat failures.
