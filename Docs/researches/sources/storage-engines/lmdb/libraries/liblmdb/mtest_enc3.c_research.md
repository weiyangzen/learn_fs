# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc3.c

## Purpose
`mtest_enc3.c` is an encrypted large-record reproducer for ITS#9920, stressing key/value sizes, encrypted page checksums, and high record counts.

## Important APIs, types, and functions
It defines `KEY_SIZE` as 24 and `MAX_VALUE_SIZE` as 150, uses deterministic `srand(42)`, installs ChaCha8 encryption with `mdb_env_set_encrypt(..., 16)`, writes 64,000 random key/value pairs, prints environment and DB stats, and performs cursor traversals and cursor-delete checks.

## Control flow
The test allocates arrays for key lengths, value lengths, keys, and values; fills them with random uppercase data; opens a 1 GiB encrypted environment; writes every generated record in one transaction with `MDB_NOOVERWRITE`; scans all records; attempts deletions; prints stats; scans forward/backward; deletes with a cursor; then verifies cursor restart behavior.

## State and persistence behavior
The program writes a large encrypted `./testdb`. The encryption checksum size parameter is specifically set to 16, with comments noting the reproduced bug occurs above lower thresholds. It uses deterministic input generation for reproducibility.

## Dependencies and integration points
It depends on `chacha8.h`, LMDB encryption APIs, and B-tree paths handling larger encrypted nodes and checksums.

## Risks and edge cases
After the initial scan, deletion sets `key.mv_data = sval` without reconstructing generated keys, so many deletes are expected to miss and do not strongly validate deletion. It can produce very large console output and requires enough disk/map space. Memory allocation failures are not checked.

## Test signals
Primary signals are no crash or corruption during 64k encrypted inserts, successful full traversal, sensible `mdb_stat` entry/depth output, and reproduction stability for ITS#9920 parameters.
