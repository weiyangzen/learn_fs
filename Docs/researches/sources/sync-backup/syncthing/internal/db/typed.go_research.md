# sources/sync-backup/syncthing/internal/db/typed.go

## Purpose
This file implements a typed, namespaced wrapper over a byte-oriented `db.KV` store.

## Important APIs and Control Flow
`Typed` stores a `KV` and namespace prefix. `NewMiscDB` uses the `misc` namespace; `NewTyped` accepts any prefix. `PutInt64` stores big-endian uint64 bytes; `Int64` reads and converts them back. `PutTime` and `Time` use `time.Time` binary marshaling. `PutString`/`String`, `PutBytes`/`Bytes`, and `PutBool`/`Bool` store simple byte encodings. `Delete` removes a prefixed key. `filterNotFound` converts `sql.ErrNoRows` into nil so missing keys return `ok=false` without an error.

## State and Persistence Behavior
All values are persisted in the underlying `KV` using keys formatted as `prefix + "/" + key`. Existing values are overwritten regardless of prior type. `Bool` stores true as `0x0` and false as `0x1`, which is unusual but internally consistent.

## Dependencies and Integration Points
It depends on the `KV` interface, `database/sql`, `encoding/binary`, and `time`. SQLite `baseDB` implements the needed KV methods. The SQLite maintenance service stores timestamps and sequence markers through this wrapper.

## Risks and Test Signals
There is no length validation before reading fixed-width int or bool values, so corrupt or wrong-type values can panic. `typed_test.go` covers namespace isolation and several value types but not bool or bytes.
