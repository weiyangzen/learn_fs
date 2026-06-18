# sources/storage-engines/rocksdb/logging/auto_roll_logger.cc

Purpose: Implementation of RocksDB `AutoRollLogger`, which wraps an underlying `Logger` and rotates LOG files by size and/or elapsed time, plus `CreateLoggerFromOptions`.

Important APIs/types/functions: constructor, `ResetLogger`, `RollLogFile`, `GetExistingFiles`, `TrimOldLogFiles`, `Logv`, `LogHeader`, `WriteHeaderInfo`, `LogExpired`, `CreateLoggerFromOptions`.

Control flow and state: construction resolves DB absolute path, computes active LOG path, renames an existing LOG, scans old info logs, opens a new logger, and trims old logs. `Logv` takes a mutex, checks time/size thresholds before writing, rolls and resets if needed, replays stored headers, trims excess files, pins the current logger in a shared pointer, releases the mutex, then writes concurrently. `RollLogFile` picks a unique old filename by timestamp, waits for pinned references, closes the old logger, renames active LOG, and enqueues it for trimming.

State and persistence behavior: persists active and rolled LOG files in DB/log directories. Keeps header strings and old-log queue in memory. Cached seconds reduce clock calls and drive time rotation.

Dependencies and integration points: `FileSystem`, `SystemClock`, filename helpers, `DBOptions`, `Env`, `Logger`, `ROCKS_LOG_WARN`, and sync points for concurrency tests.

Risks: busy-waits on `logger_.use_count() > 1`; rename errors inside `RollLogFile` are ignored. Header serialization truncates at 1024 bytes. Old-log deletion bypasses DB rate limiting and directory sync. `Logv` asserts status ok.

Test signals: covered by auto-roll logger tests for size/time rolling, trimming, headers, create failures, rename races, info log levels, and flush while rolling.
