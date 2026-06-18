# sources/sync-backup/git-lfs/lfs/config.go

Purpose: centralizes fetch/prune-related Git LFS configuration with defaults.

Important APIs/types/functions: `FetchPruneConfig` and `NewFetchPruneConfig`.

Control flow: reads keys from `config.Environment`, defaults prune remote to `origin`, and fills integer/boolean fields for recent refs, recent commits, prune offsets, remote verification, and flags initialized for command overrides.

State/persistence behavior: read-only config snapshot in memory.

Dependencies/integration: used by `lfs.Environ` and fetch/prune commands to expose consistent policy.

Risks/test signals: typo in comments only (`verifiying`). Tests cover default and custom config values.
