# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_open.go

## Purpose
This file defines the per-folder database type and opens folder-specific SQLite databases.

## Important APIs and Types
`folderDB` embeds `*baseDB` and stores `folderID`, `localDeviceIdx`, and `deleteRetention`. `openFolderDB` configures normal folder pragmas, common and folder schemas/migrations, opens the base DB, writes `folderID` to KV, creates/touches the local device row, and stores `LocalDeviceIdx` in template input. `openFolderDBForMigration` uses unsafe bulk-insert pragmas, one connection, and no migrations. `deviceIdxLocked` upserts a device string into `devices` and returns its numeric `idx`.

## State and Persistence Behavior
Opening creates or migrates the folder database file, initializes common tables, ensures the local device row exists, and records folder identity in KV. Device indexes become stable internal foreign keys for files, counts, and index IDs.

## Dependencies and Integration Points
It integrates with `openBase`, schema assets, application IDs, `protocol.LocalDeviceID`, and `folderDB` methods that use `{{.LocalDeviceIdx}}` in SQL templates.

## Risks and Test Signals
Device index stability matters because lower device indexes influence conflict tie-breaking. Bulk migration mode must not be used for normal operation. Most tests cover this indirectly through every folder operation.
