# sources/sync-backup/syncthing/internal/db/olddb/smallindex.go

## Purpose
This file implements a small in-memory bidirectional index used by the legacy database reader to map persisted uint32 IDs to folder/device string values.

## Important APIs, Control Flow, And State
`smallIndex` holds a backend, key prefix, `id2val`, `val2id`, `nextID`, and mutex. `newSmallIndex` constructs maps and immediately calls `load`. `load` scans the prefix key space, decodes the uint32 ID from the key suffix, stores non-empty values in both maps, and advances `nextID` past the largest observed ID. `ID` returns an existing ID for a value or panics on missing values. `Val` returns the value for an ID. `Values` returns sorted values.

## State And Persistence
Persistent state is stored in old LevelDB index key spaces. Empty values are treated as deleted entries. Runtime state is an in-memory cache protected by a mutex.

## Dependencies And Integration Points
It depends on `encoding/binary`, `slices`, `sync`, and the old backend. `defaultKeyer` uses these indexes to encode and decode old compound keys.

## Risks And Test Signals
`ID` no longer allocates or persists missing IDs despite its older comment, and instead panics. That is appropriate for read-only migration but should be documented in callers. `load` panics on iterator creation failure and does not check `it.Error()` after iteration, so load-time iterator errors may be missed. Tests should cover deleted entries, sorted values, ID/Val round trips, missing ID panic, and iterator error behavior.
