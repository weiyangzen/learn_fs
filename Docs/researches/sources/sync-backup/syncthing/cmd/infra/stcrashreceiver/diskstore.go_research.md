# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/diskstore.go

Purpose: asynchronous compressed disk-backed storage for crash reports, with inventory and retention limits by file count and byte size.

Important APIs/types/functions: `diskStore`, `diskEntry`, `currentFile`, methods `Serve`, `Put`, `Get`, `Exists`, `clean`, `inventory`, and `fullPath`. It stores reports as gzip files under a two-character shard directory.

Control flow: `Serve` creates the directory, inventories existing `.gz` files, cleans over-budget files, then loops on inbox writes, minute cleanup ticks, daily inventory ticks, and context cancellation. Incoming reports are gzip-compressed into a reusable buffer and written to disk. `Put` is non-blocking and returns false when the queue is full. `Get` reads and decompresses. `clean` deletes oldest files until under limits.

State and persistence behavior: persists compressed reports on disk. In-memory `currentFiles` and `currentSize` cache inventory and are updated by writes/clean/inventory.

Dependencies/integration: used by `crashReceiver` HTTP handlers and metrics gauges. Relies on `os`, `gzip`, `filepath.Walk`, `slices.SortFunc`, and Prometheus metrics.

Risks/test signals: newly appended `currentFile.size` uses uncompressed `len(entry.data)` while `currentSize` adds compressed length, so cleanup accounting can drift until inventory. Paths assume report IDs have at least two characters. Signals are successful PUT/GET round trips, retention deleting oldest reports, and diskstore metrics matching inventory after daily refresh.
