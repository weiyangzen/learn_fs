# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/debug.py

## Purpose
Defines `tahoe debug` tools for inspecting caps and share files, locating/cataloging shares, deliberately corrupting test shares, and invoking Foolscap `flogtool` with Tahoe imports.

## APIs, Types, And Control Flow
Command options include `DumpOptions`, `DumpCapOptions`, `FindSharesOptions`, `CatalogSharesOptions`, `CorruptShareOptions`, `FlogtoolOptions`, and `DebugCommand`. `dump_share` detects mutable versus immutable share headers and dispatches to parsers. Immutable parsing uses `ShareFile` and `ReadBucketProxy` to extract URI extension data, leases, offsets, and verify caps. Mutable parsing reads lease/header metadata and handles SDMF via `unpack_share` or MDMF via a local `MDMFSlotReadProxy`. `dump_cap` parses URI strings or `/uri/` URLs and prints keys, storage indexes, fingerprints, verifier details, and optional lease secrets. `find_shares` and `catalog_shares` scan storage share directories. `corrupt_share` flips a random data bit in supported share types for checker/repair testing.

## State, Persistence, And Integration
Mostly read-only inspection of share files and node storage directories. `corrupt_share` mutates a share in place with `rb+`. The module integrates tightly with storage layout internals, mutable layout parsers, URI classes, hash utilities, Foolscap logging CLI, and Twisted Deferred helpers.

## Risks And Test Signals
This is intentionally low-level and brittle: offset calculations duplicate storage internals, malformed shares can raise while cataloging, `corrupt-share` is destructive, and some code only supports SDMF mutable corruption. Test signals are debug CLI tests, storage layout tests, checker/repair tests that use corrupted shares, and manual diagnostics against test grids.
