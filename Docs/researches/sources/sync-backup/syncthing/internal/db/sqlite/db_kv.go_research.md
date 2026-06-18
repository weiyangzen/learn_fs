# sources/sync-backup/syncthing/internal/db/sqlite/db_kv.go

## Purpose
This file implements the low-level SQLite-backed `db.KV` operations on `baseDB`, providing a simple `kv` table for metadata and typed wrappers.

## Important APIs and Control Flow
`GetKV` selects a byte value by key and wraps any SQL error. `PutKV` and `DeleteKV` acquire `baseDB.updateLock` before mutating `kv` with `INSERT OR REPLACE` or `DELETE`. `PrefixKV` returns an `iter.Seq[db.KeyValue]` plus error function. With an empty prefix it scans all key/value rows; otherwise it uses `prefixEnd(prefix)` to construct a lexicographic half-open range.

## State and Persistence Behavior
State lives in the common `kv` table present in both main and folder databases. Values are opaque byte slices; namespaces and typed encodings are layered by `internal/db/typed.go`. Iterators close SQL rows when iteration exits and defer row-scan errors to the returned error function.

## Dependencies and Integration Points
This file depends on `sqlx.Rows`, `db.KeyValue`, `baseDB.stmt`, `baseDB.updateLock`, `wrap`, and `prefixEnd` from `util.go`. It supports service metadata such as maintenance timestamps and folder metadata such as `folderID`.

## Risks and Test Signals
The prefix range relies on binary-collated string ordering and a non-empty prefix. `GetKV` intentionally surfaces `sql.ErrNoRows`; typed callers convert that to a missing-value result. Tests in `typed_test.go` indirectly exercise put/get/delete behavior.
