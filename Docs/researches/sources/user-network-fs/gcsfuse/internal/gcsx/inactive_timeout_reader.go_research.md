## sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader.go

Purpose: wraps a `gcs.StorageReader` and closes the underlying GCS reader after inactivity, reconnecting later from the last consumed offset with a read handle.

Important APIs/types/functions: `InactiveTimeoutReader`, `ErrZeroInactivityTimeout`, `NewInactiveTimeoutReader`, `NewInactiveTimeoutReaderWithClock`, `createGCSReader`, `Read`, `Close`, `ReadHandle`, `monitor`, `handleTimeout`, and `closeGCSReader`.

Control flow: construction rejects zero timeout, creates an initial reader with `NewReaderWithReadHandle`, derives a cancellable context, and starts a monitor goroutine. `Read` locks, marks active, recreates the GCS reader if timeout closed it, reads, and advances `seen`. The monitor wakes every timeout duration; active readers have `isActive` reset, inactive readers are closed. `Close` cancels the monitor and closes any open reader.

State/persistence behavior: tracks requested byte range, bytes seen, last read handle, active flag, and current reader. It does not persist data locally. Reconnect starts at `reqRange.Start + seen` and preserves the original limit.

Dependencies/integration: uses `gcs.Bucket.NewReaderWithReadHandle`, GCS byte ranges, storage v2 read handles, internal `clock` for tests, `locker`, and logger. It is suitable for many idle range readers while preserving efficient resumability.

Risks/test signals: the monitor closes between one and two timeout durations after last read, by design. Reads after explicit `Close` are unsupported. Locking serializes concurrent reads. Tests cover zero timeout, initial error, timeout close, reconnect success/failure, read handle preservation, close behavior, and a race-style concurrent read/timeout scenario.
