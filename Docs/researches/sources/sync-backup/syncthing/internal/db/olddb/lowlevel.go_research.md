# sources/sync-backup/syncthing/internal/db/olddb/lowlevel.go

## Purpose
This file creates the low-level legacy database wrapper around a backend and exposes folder listing plus virtual mtime iteration.

## Important APIs, Control Flow, And State
`deprecatedLowlevel` embeds `backend.Backend` and holds `folderIdx`, `deviceIdx`, and the `keyer`. `NewLowlevel` constructs small indexes for folder and device index key spaces and creates a default keyer. `ListFolders` returns sorted folder index values. `IterateMtimes` scans keys with `KeyTypeVirtualMtime`, decodes the folder ID from the key, treats the remainder as the filename, splits the value into two binary-marshaled `time.Time` values, and calls the supplied callback for each valid mapping.

## State And Persistence
State is read from the old LevelDB backend and cached in small indexes. Virtual mtime values are persisted as concatenated binary time encodings.

## Dependencies And Integration Points
It depends on `encoding/binary`, `time`, and the legacy backend. Migration code can use it to enumerate folders and mtime mappings from old databases.

## Risks And Test Signals
`IterateMtimes` silently skips unknown folder IDs and time-unmarshal failures, which keeps migration robust but can hide data loss. It assumes values split exactly into two binary time encodings. Tests should cover folder index loading, sorted `ListFolders`, valid mtime decoding, invalid values, unknown folder IDs, callback error propagation, and iterator errors.
