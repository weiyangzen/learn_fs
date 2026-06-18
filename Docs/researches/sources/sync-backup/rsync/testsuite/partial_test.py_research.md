## sources/sync-backup/rsync/testsuite/partial_test.py

Purpose: comprehensive coverage for `--partial` and relative/absolute `--partial-dir` at deep paths and across directory boundaries.

Important APIs and control flow: `seed_big()` creates a large deep file. `is_prefix()` validates partial contents. `interrupt_transfer(extra_args, partial_path)` starts a throttled delta transfer, polls for an in-progress temp file, sends SIGTERM, then waits for the expected partial. The test covers plain `--partial` resume, relative partial-dir preseed and cleanup, relative partial-dir interrupt/resume, absolute partial-dir outside the destination tree, and absolute partial-dir delta resume consuming the basis.

State and dependencies: uses `subprocess.Popen`, signals, polling deadlines, `SCRATCHDIR/partials`, and direct file prefix checks.

Integration points: receiver cleanup, partial storage resolution, delta basis opening, and verification after interrupted transfers.

Risks and test signals: timing-sensitive under heavy load, mitigated by low bandwidth and long deadlines. Signals include valid partial prefix, final content equality, and partial-dir cleanup.
