# sources/sync-backup/syncthing/internal/db/olddb/transactions.go

## Purpose
This file implements read-only legacy transactions that unmarshal old database file records and follow indirections for block lists and version vectors.

## Important APIs, Control Flow, And State
`readOnlyTransaction` embeds `backend.ReadTransaction` and carries a `keyer`. `deprecatedLowlevel.newReadOnlyTransaction` opens a backend snapshot and wraps it. `getFileByKey` and `getFileTrunc` fetch bytes by key, translate not-found to `(false, nil)`, unmarshal full or truncated file info, and fill indirect data. `unmarshalTrunc` handles `dbproto.FileInfoTruncated` or BEP `FileInfo`. `fillFileInfo` loads block lists through `BlocksHash` and version vectors through `VersionHash`. `fillTruncated` loads only version vectors. `withHaveSequence` creates sequence range keys from `startSeq` to `maxInt64`, iterates sequence entries, resolves each value as a device-file key, and calls the supplied iterator.

## State And Persistence
It reads old persisted protobuf records, indirect block-list records, and version-vector records. It does not mutate state.

## Dependencies And Integration Points
It depends on protobuf, generated BEP/dbproto types, protocol conversion helpers, and the old backend. It is used by `deprecatedFileSet` snapshots and migration code.

## Risks And Test Signals
Missing indirect block lists are wrapped in `blocksIndirectionError`, while missing top-level files are skipped. Corrupt protobuf values abort iteration. Sequence index values must point to valid file keys. Tests should cover full and truncated unmarshalling, missing/corrupt block and version indirections, range iteration boundaries, early iterator stop, and backend iterator errors.
