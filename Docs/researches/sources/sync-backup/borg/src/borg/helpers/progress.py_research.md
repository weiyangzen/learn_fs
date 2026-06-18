# sources/sync-backup/borg/src/borg/helpers/progress.py

## Purpose
Emits machine-readable progress messages and percentage updates through the Borg progress logger.

## Important APIs, Types, And Functions
`ProgressIndicatorBase` provides logger setup, unique `operation_id`, `make_json`, and `finish`. `ProgressIndicatorMessage.output` emits arbitrary progress messages. `ProgressIndicatorPercent` tracks total, counter, percentage step, formatting message, `progress`, `show`, and `output`.

## Control Flow
Each instance receives a monotonically increasing operation id. `make_json` adds operation id, message id, JSON type, finished flag, and current wall time. Percent progress computes `counter * 100 / total`, increments the counter, and emits only when the threshold `trigger_at` is reached, then advances the threshold.

## State And Persistence
State is in-memory per indicator plus class-level `operation_id_counter`. Output is logged to `borg.output.progress` as JSON lines; no files are written here.

## Dependencies And Integration Points
Used by commands that need structured progress output and by frontends consuming Borg logs. Depends on standard logging/json/time and Borg logger setup.

## Risks And Edge Cases
`ProgressIndicatorPercent` divides by `total`, so callers must avoid zero totals when showing progress. Class-level operation ids are process-local and not reset except by test manipulation. JSON messages include wall-clock time, making exact-output assertions brittle.

## Test Signals
Existing progress tests should cover message JSON shape, finish events, percent thresholds, counter increments, info payload formatting, operation id increments, and logger integration.
