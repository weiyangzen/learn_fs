# sources/sync-backup/git-lfs/tq/meter.go

Purpose: progress meter for transfer queues, including tasklog updates and optional `GIT_LFS_PROGRESS` file logging.

Important APIs/types/functions: `Meter`, `LoggerFromEnv`, `LoggerToFile`, `NewMeter`, `Start`, `Pause`, `Add`, `Skip`, `StartTransfer`, `TransferBytes`, `FinishTransfer`, `Flush`, `Finish`, `Updates`, `Throttled`, `str`, `clamp`, `clampf`, and `logBytes`.

Control flow: transfer queue calls `Add`/`Skip`/`StartTransfer`/`TransferBytes`/`FinishTransfer`; each triggers `update` unless dry-run, paused, or no estimated files. `TransferBytes` updates byte totals and rolling average once per second. File logging writes direction, file index, counts, bytes, and name through `SyncWriter`.

State and persistence: atomic counters, average sample state, file-index map with mutex, updates channel, optional sync logger file.

Dependencies and integration points: used by `TransferQueue` and adapters for CLI progress; uses `tools/humanize`, `tasklog`, and config for progress-log directory creation.

Risks: `update` sends on an unbuffered channel and can block if no consumer is reading. `str` reads atomic fields directly in places rather than all via atomic loads. Logger disables itself on write error.

Test signals: no direct meter tests in this subset; progress behavior is indirectly exercised by queue/adapter flows.
