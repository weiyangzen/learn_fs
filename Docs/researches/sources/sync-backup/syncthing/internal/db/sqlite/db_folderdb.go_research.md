# sources/sync-backup/syncthing/internal/db/sqlite/db_folderdb.go

## Purpose
This file implements the top-level SQLite `DB` methods that delegate folder-scoped file-index operations to lazily opened per-folder databases.

## Important APIs, Control Flow, And State
`getFolderDB(folder, create)` checks the open-folder map, reads or creates a folder database name in the main `folders` table, creates a new name from folder index plus random slug when needed, opens the folder DB, and caches it. `Update` applies `db.UpdateOption` values and delegates to `folderDB.Update`. The remaining methods delegate block index, file lookup, global/local iterators, needed-file iterators, cleanup, device lists, remote sequences, counts, index IDs, device sequences, mtime mapping, debug output, and folder/device drops to the appropriate folder DB. Missing folders usually return empty iterators, zero counts, nil slices/maps, false lookups, or nil errors. `forEachFolder` iterates all known folders and runs a callback, retaining the first error.

## State And Persistence
The main DB stores folder IDs and per-folder database filenames. Each folder DB stores file, block, sequence, count, index ID, and mtime data for that folder. Folder DBs are opened lazily and cached in `s.folderDBs` under `folderDBsMut`; creation also uses `updateLock`.

## Dependencies And Integration Points
It depends on `internal/db`, config pull ordering, protocol IDs, logging, random slugs, and `folderDB` methods implemented in other SQLite files. It is the concrete implementation of much of `db.DB`.

## Risks And Test Signals
Missing-folder behavior varies slightly by return type and includes `nil, nil` for some slices/maps; callers must tolerate that. Lazy creation means read paths should pass `create=false` to avoid accidental persistent state. Folder DB filename uniqueness depends on folder index plus random slug. Tests should cover concurrent `getFolderDB`, missing-folder read semantics, creation persistence, all delegated methods, `forEachFolder` first-error handling, and mtime/index ID behavior.
