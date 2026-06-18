<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_set.go -->
# sources/sync-backup/kopia/cli/command_repository_throttle_set.go

Purpose: implements `repository throttle set`, changing direct repository throttling limits.

Important APIs/types/functions: `commandRepositoryThrottleSet`, `commonThrottleSet`, `repo.DirectRepositoryWriter`, `Throttler().Limits`, `cts.apply`, and `Throttler().SetLimits`.

Control flow: setup registers common throttle-set flags and a direct repository write action. `run` copies current limits, applies requested flag changes while counting mutations, logs no-op when nothing changed, and persists the new limits through the throttler.

State/persistence behavior: mutates repository throttler limits. The limits affect repository blob/content IO throttling after the update.

Dependencies/integration: shares validation and parsing with server throttle setters. Risks/test signals: only changed when common helper increments change count; invalid negative values are rejected by helper logic before persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_set.go -->
