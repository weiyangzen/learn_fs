## sources/sync-backup/syncthing/lib/protocol/counting.go

Purpose: wraps readers and writers to maintain protocol-wide byte counters and last-activity timestamps.

Important types/functions: `countingReader`, `countingWriter`, global `totalIncoming`/`totalOutgoing` counters, methods `Read`, `Write`, `Tot`, `Last`, and `TotalInOut`.

Control flow and state: read/write methods delegate to the wrapped object, add successful byte counts to both instance and global atomics, and update last activity time. `Tot` reads per-wrapper total; `Last` reads the timestamp.

Dependencies and integration points: used by raw protocol connections for statistics and activity reporting.

Risks: only successful byte counts are tracked; partial reads/writes with errors count bytes returned by the underlying call. Time fields must be concurrency-safe through their type implementation.

Test signals: no direct tests in this subset; connection benchmarks exercise counters indirectly.
