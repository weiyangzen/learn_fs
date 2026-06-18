# sources/sync-backup/restic/internal/ui/stats/progress_test.go

Purpose: validates the stats progress formatter without starting the updater scheduler.

Important APIs/types/functions: `TestStatsProgress` drives `newProgress`, `ProcessSnapshot`, `Update`, and `printProgress`; `TestStatsProgressJSON` verifies `show=false`.

Control flow: tests use `ui.MockTerminal` to inspect the last status or printed output. The main test steps through initial state, first snapshot processing, second snapshot processing, additional counters, and final output.

State and persistence: no persistent state; checks in-memory terminal output slices.

Dependencies/integration: imports restic's test helper aliases and `ui.MockTerminal`, giving a focused unit test for the stats package's terminal contract.

Risks: the tests assert exact human-readable strings, so intentional format changes require test updates. They do not exercise `NewProgress` interval calculation or actual goroutine timing.

Test signals: strong formatting regression coverage for percent behavior, counter reset, byte formatting, and JSON suppression.
