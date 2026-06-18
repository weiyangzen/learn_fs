# sources/user-network-fs/rclone/cmd/ncdu/scan/scan.go

Purpose: concurrently scans an rclone Fs into an in-memory directory tree with accumulated size/count metadata for ncdu.

Important APIs/types: `Dir`, `Attrs`, `AverageSize`, `Parent`, `Path`, `newDir`, `Entries`, `Remove`, `GetDir`, `Attr`, `AttrI`, `AttrWithModTimeI`, and `Scan`.

Control flow: `Scan` starts a goroutine running `walk.Walk`; each walked directory creates a `Dir`, attaches to its parent via a map, sends root once, and signals coalesced updates. `newDir` counts file sizes, tracks unknown sizes, stores read errors, and propagates totals/error flags to parents. `Remove` updates entries, child directory map, and parent totals after UI deletions.

State/persistence: all state is in-memory and protected by per-Dir mutexes for mutable totals/entries. It reads remotes but does not mutate them. Dependencies are `fs/walk`, `fs.DirEntries`, slices, sync. Risks include sending multiple errors on a buffered channel of size one, parent lookup assumptions based on walk order, and partial tree accuracy when read errors occur. Tests cover size/count propagation, unknown sizes, attrs, removal, and scan basics.
