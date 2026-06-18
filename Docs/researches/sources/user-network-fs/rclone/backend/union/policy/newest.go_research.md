# sources/user-network-fs/rclone/backend/union/policy/newest.go

Purpose: selects the candidate with the newest modification time.

Important APIs: `Newest`, registered as `newest`; helpers `newest` and `newestEntries`; action/create/search methods.

Control flow/state: concurrently probes upstream entries and modtimes, chooses the max timestamp, filters writable/creatable candidates by category, and for create compares parent paths. Entry variant uses a five-second background timeout.

Dependencies/integration: `context`, `path`, `sync`, `time`, `upstream`, `fs`; depends on `findEntry` and backend modtime precision.

Risks/test signals: weak modtime precision, slow `ModTime`, and non-propagated caller cancellation in `newestEntries`. Coverage is indirect.
