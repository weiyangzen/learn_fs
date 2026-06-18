# sources/user-network-fs/rclone/backend/hasher/commands.go

## Purpose
This file implements backend commands for the hasher overlay: dropping the checksum cache, dumping cache contents, and importing checksum files.

## Important APIs, Types, And Control Flow
`Command` dispatches `drop`, `dump`, `fulldump`, `import`, and `stickyimport`. `drop` stops and deletes the kv database. Dumps call `dbDump`, with `fulldump` including records outside the current wrapped root. Imports validate the hash type, ignore unsupported or unneeded hashes, open a SUM file through rclone's cache, parse it with `operations.ParseSumFile`, and either write sticky records with `anyFingerprint` or walk the wrapped hasher filesystem to bind checksums to existing objects by path.

`commandHelp` documents command usage. `dbDump` resolves the wrapped remote root when needed, handles disabled or inactive DBs, and delegates to `kvDump`. `dbImport` logs long imports, records checking transfers for non-sticky imports, and reports skipped vanished objects.

## State And Persistence
The commands read and mutate the hasher kv database. `drop` removes cached state, `import` writes records, and dumps print database content to stdout/logs. Sticky imports intentionally persist hash records without fingerprint validation.

## Dependencies And Integration Points
It depends on rclone `fs.Commander`, `cache.Get`, `fspath`, `hash.Type`, `operations.ParseSumFile`, `operations.ListFn`, `accounting`, and `kv`. It relies on object-level `putHashes` and filesystem `putRawHashes` implemented elsewhere in the hasher package.

## Risks And Test Signals
Risks include importing stale or mismatched checksum files, sticky import bypassing size/time fingerprint checks, disabled DB when `max_age=0`, large import performance, and partial failures being logged rather than fatal per object. Tests should cover command dispatch, bad args, unsupported hash types, inactive DB, dump formatting, sticky and non-sticky import semantics, and vanished objects.
