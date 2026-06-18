<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle.go -->
# sources/sync-backup/kopia/cli/command_repository_throttle.go

Purpose: groups repository throttling subcommands under `repository throttle`.

Important APIs/types/functions: `commandRepositoryThrottle`, `commandRepositoryThrottleGet`, `commandRepositoryThrottleSet`, and `setup`.

Control flow: setup creates the parent command and delegates registration to `get` and `set`. There is no execution logic in this file.

State/persistence behavior: none directly; child commands read or mutate throttler limits on the active direct repository.

Dependencies/integration: thin command-tree integration point. Risks/test signals: if either child setup is omitted, throttle operations become unreachable despite their implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle.go -->
