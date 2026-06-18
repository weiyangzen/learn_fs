# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc4.c

## Purpose
`mtest_enc4.c` creates an encrypted database with varied large value sizes to exercise encrypted overflow-page handling, especially for ITS#10520 and follow-up dump/load/copy validation.

## Important APIs, types, and functions
It uses `mdb_modload`, `mdb_modsetup`, and `mdb_modunload` with `crypto.lm`, sets a 1 GiB map, writes 2,400 records with up to 64 KiB values, commits every 100 records, and uses `MDB_NOOVERWRITE`.

## Control flow
The program loads the crypto module with a hardcoded passphrase, opens `./testdb`, starts a write transaction, repeatedly generates an 8-byte random hex key and random value size, points data at a shared `valbuf`, writes the record, and commits/restarts the transaction every 100 iterations. It prints duplicate counts, commits the final batch, gathers environment stats, then closes and unloads the module.

## State and persistence behavior
The output is an encrypted database containing values large enough to occupy overflow pages. Batching commits means partial progress persists if a later batch fails. The comment directs operators to run dump/load/copy tools afterward to verify encrypted overflow correctness.

## Dependencies and integration points
This file integrates module-based crypto with LMDB overflow-page allocation and with the utility suite (`mdb_dump`, `mdb_load`, `mdb_copy`) as downstream validation.

## Risks and edge cases
`data.mv_size` may be zero because `rand() % MAX_VALUE_SIZE` includes zero. Only the start of `valbuf` is formatted; the rest may contain previous data or zeros. Error paths after module load may skip unload. Random keys can collide.

## Test signals
Successful creation plus successful encrypted dump/load/copy round trips are the main signals. Additional validation should compare record counts and large-value contents after copy/load.
