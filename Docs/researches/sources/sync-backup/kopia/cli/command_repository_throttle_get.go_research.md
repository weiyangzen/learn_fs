<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_get.go -->
# sources/sync-backup/kopia/cli/command_repository_throttle_get.go

Purpose: implements `repository throttle get`, displaying current repository throttling limits.

Important APIs/types/functions: `commandRepositoryThrottleGet`, `commonThrottleGet`, `repo.DirectRepository`, `rep.Throttler().Limits`, and `ctg.output`.

Control flow: setup registers common output flags and a direct repository read action. `run` obtains current throttler limits and delegates text/JSON output formatting to the shared throttle output helper.

State/persistence behavior: read-only over runtime/repository throttler state.

Dependencies/integration: depends on direct repository access and common throttle formatting shared with server throttling. Risks/test signals: output behavior is covered by repo and server throttle integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_get.go -->
