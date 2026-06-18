<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/accounting-reader.go -->
# sources/object-store/minio-mc/cmd/accounting-reader.go

## Purpose
Progress accounting helper implementing an `io.Reader`-like counter for transfer operations and formatted/JSON reporting of total, transferred bytes, duration, and speed.

## Important APIs, types, and functions
`accounter` stores atomically updated current/total counters, timing, refresh rate, and a finish channel. Functions/methods include `newAccounter`, `write`, `writer`, `Stat`, `Update`, `Set`, `Get`, `SetTotal`, `Add`, and `Read`. `accountStat` implements `String` and `JSON`.

## Control flow
Creation starts a goroutine that periodically calls `Update` until `Stat` closes `isFinished` once. `Read` increments by buffer length and caps current to total on deferred cleanup to handle upload retries.

## State and persistence behavior
State is in-memory and atomic; no disk persistence. `Stat` finalizes the goroutine and returns a snapshot.

## Dependencies and integration points
Uses colorized console tables, `cheggaaa/pb` formatting, MinIO probe errors, and colorjson. Used by transfer commands needing accounting without wrapping an underlying reader.

## Risks and test signals
`Read` counts the requested buffer length, not bytes from an underlying source, so it is a counter shim rather than a real reader wrapper. Tests should cover concurrent Add/Get, total cap behavior, JSON/String formatting, and goroutine shutdown through `Stat`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/accounting-reader.go -->
