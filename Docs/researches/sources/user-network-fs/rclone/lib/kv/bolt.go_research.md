# sources/user-network-fs/rclone/lib/kv/bolt.go

Source read signal: reviewed complete local file (320 lines, sha256 49ca1d74390c8dd3).

Purpose: Implements a process-shared, reference-counted bbolt key/value database for supported platforms.

Important APIs/types/functions: `DB` holds name/path/facility/ref count, bbolt handle, timers, queue, lock settings, and write mode. Public APIs are `Supported`, `Start`, `Get`, `Path`, `Do`, `Stop`, `IsStopped`, and `Exit`; helpers include `makeName`, `open`, `close`, `loop`, `request.handle`, and `execute`.

Control flow: `Start` reuses existing DBs by name, creates the cache directory, opens read-only if possible, registers the DB, and starts a serialized request loop. `Do` enqueues a request and waits. The loop handles requests, idle/lock timers that close the bbolt handle, and stop requests that decrement refs and optionally remove the DB file. `execute` opens for read/write and runs a bbolt view or update against the facility bucket.

State and persistence behavior: Persists data under `config.GetCacheDir()/kv/<encoded-name>.bolt` mode 0600, directory 0700. Maintains process-global `dbMap`, refs, timers, and at-exit shutdown state.

Dependencies and integration points: Uses bbolt, rclone config/cache settings, `encoder.OS` for safe DB filenames, and `fs.GetConfig` retry/lock durations. Callers implement `Op` over abstract `Bucket`/`Cursor`.

Risks and test signals: Queue size is small and `Do` can block if the loop stops after the nil check. `IsStopped` checks global map length, not this DB specifically. Cross-process bbolt locks and timer-close behavior need careful testing; unit tests cover concurrent `Start` refs and `Exit`.
