<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_scheduling.go -->
# sources/sync-backup/kopia/cli/command_policy_set_scheduling.go

Purpose: implements scheduling policy flags for interval snapshots, times of day, crontab expressions, missed-run behavior, and manual-only snapshots.

Important APIs/types/functions: `policySchedulingFlags`, `setSchedulingPolicyFromFlags`, `setScheduleFromFlags`, `setRunMissedFromFlags`, `splitCronExpressions`, `setManualFromFlags`, `policy.TimeOfDay`, and `policy.ValidateSchedulingPolicy`.

Control flow: setup registers duration-list interval, comma-separated times, semicolon-separated cron, `run-missed`, and `manual`. Manual mode rejects simultaneous schedule flags, clears existing interval/times/cron, then sets `Manual`. Schedule mode applies first interval value, parses and deduplicates times, splits cron entries, validates cron policy, applies `run-missed`, and clears prior manual mode.

State/persistence behavior: stores interval seconds, sorted time-of-day slices, cron slices, optional `RunMissed`, and manual bool in the policy. `inherit`/`default` clears time or cron slices.

Dependencies/integration: consumed by server/KopiaUI scheduled snapshots. Risks/test signals: only the first interval list value is used; comment-only cron expressions are preserved and validated by policy logic.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_scheduling.go -->
