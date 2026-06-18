# sources/sync-backup/borg/src/borg/testsuite/helpers/progress_test.py

Purpose: tests percentage progress indicator output cadence and quiet mode.

Important APIs and control flow: tests instantiate `ProgressIndicatorPercent` with totals, steps, starts, and message format, set logger level, call `show` with explicit or implicit current values, and call `finish`. They assert initial, stepped, final, and trailing newline stderr output. Quiet mode sets logger level to WARN and expects no output.

State and persistence: in-memory indicator state tracks current progress and last emitted percentage. Captured stderr is the observable state.

Dependencies and integration points: depends on `helpers.progress.ProgressIndicatorPercent` and pytest `capfd`. It integrates with CLI progress reporting.

Risks: output formatting is exact, including spaces and final newline. Logger level controls visibility.

Test signals: exact captured stderr strings and silence in quiet mode.
