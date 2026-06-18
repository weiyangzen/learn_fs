
# sources/user-network-fs/rclone/lib/batcher/options.go

Purpose: exposes batcher settings as rclone backend options.

Important APIs/types/functions: `(*Options).FsOptions(extra string) []fs.Option` returns option definitions for `batch_mode`, `batch_size`, `batch_timeout`, and hidden legacy `batch_commit_timeout`.

Control flow: builds help text with configured max/default values and caller-provided extra documentation.

State/persistence: no state; declarative option metadata.

Dependencies/integration: depends on rclone `fs.Option` and `fs.Duration`; backend config structs can embed/use these options.

Risks: help text must stay aligned with actual `batcher.New` behavior. Hidden `batch_commit_timeout` is retained for compatibility and no longer used.

Test signals: indirectly covered by backends parsing options and by batcher constructor tests.
