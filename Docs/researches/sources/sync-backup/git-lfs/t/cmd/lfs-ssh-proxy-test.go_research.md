# sources/sync-backup/git-lfs/t/cmd/lfs-ssh-proxy-test.go

Purpose: minimal executable used to prove SSH proxy command invocation.

Important API: `main`.

Control flow: prints `SSH PROXY TEST called` and exits.

State/persistence behavior: none.

Dependencies/integration: used by tests that configure proxy-like SSH commands.

Risks: no argument validation; it is intentionally only a sentinel.

Test signals: stdout string confirms the configured command was invoked.
