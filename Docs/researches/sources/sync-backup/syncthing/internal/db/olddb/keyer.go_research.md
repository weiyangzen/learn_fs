# sources/sync-backup/syncthing/internal/db/olddb/keyer.go

## Purpose
This file defines the legacy LevelDB key format and key construction/parsing helpers for old Syncthing database data.

## Important APIs, Control Flow, And State
The constants define prefix lengths and key type bytes for device files, global versions, block maps, statistics, virtual mtimes, folder/device indexes, index IDs, folder metadata, misc data, sequence index, need index, block lists, version vectors, and pending devices/folders. The `keyer` interface describes all key operations. `defaultKeyer` uses `smallIndex` maps for folder and device string-to-uint32 IDs. Each generated key writes a type byte and big-endian indexed IDs, hashes, sequence numbers, or names into a reused/resized byte slice. Typed key aliases expose prefix slicing helpers such as `WithoutName`, `WithoutHashAndName`, `Hash`, and `WithoutSequence`.

## State And Persistence
The key format is the persistent schema for legacy LevelDB data. Folder and device IDs are stored in small index key spaces and referenced by uint32 in compound keys. The `resize` helper allows efficient buffer reuse during scans.

## Dependencies And Integration Points
It depends on `encoding/binary` and the old `smallIndex`. Legacy transactions use it to generate range boundaries and dereference file records, block lists, versions, mtimes, and pending state.

## Risks And Test Signals
Key parsing assumes correct key lengths and will panic on malformed short keys. `smallIndex.ID` now panics for missing IDs, suitable for read-only migration when indexes must already exist but dangerous if used for writes. `DeviceFromIndexIDKey` appears to use `folderIdx.Val` instead of `deviceIdx.Val`, which is a notable correctness risk unless intentionally preserving a legacy quirk. Tests should pin exact byte layouts, range prefix helpers, round trips for all key types, malformed key handling, and the index-ID device parser behavior.
