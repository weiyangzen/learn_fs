# sources/sync-backup/restic/internal/ui/stats/progress.go

Purpose: implements the progress reporter used by restic's `stats` command.

Important APIs/types/functions: `Progress` embeds `progress.Updater`; `NewProgress()` wires update cadence via `progress.CalculateProgressInterval`; `Update()` accumulates file/blob/byte counters; `ProcessSnapshot()` advances snapshot count and resets per-snapshot counters; `printProgress()` formats terminal status.

Control flow: construction decides whether progress should display based on quiet/json/status capability. Periodic updater calls `printProgress`; non-final output goes to `Terminal.SetStatus`, while final output clears status and prints a normal line.

State and persistence: guarded by `sync.Mutex`; counts are in-memory only. `processedSnapshotCount` is displayed directly, while percent uses one less snapshot during active processing so the current snapshot does not count complete until final.

Dependencies/integration: depends on `internal/ui` formatting helpers and `internal/ui/progress` scheduling. Integrates with any `ui.Terminal`.

Risks: snapshot denominator zero behavior is delegated to `ui.FormatPercent`; concurrent `Update()` and updater callbacks rely on correct mutex use.

Test signals: `progress_test.go` verifies formatting, per-snapshot reset, final 100 percent output, and suppressed JSON mode.
