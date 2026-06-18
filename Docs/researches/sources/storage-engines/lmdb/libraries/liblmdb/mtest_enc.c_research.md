# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc.c

## Purpose
`mtest_enc.c` adapts the basic main-database test to an encrypted LMDB environment using an in-process ChaCha8 encryption callback.

## Important APIs, types, and functions
`encfunc` calls `chacha8` with source, destination, encryption key material, and IV-like key slots. `main` configures the environment with `mdb_env_set_encrypt`, then follows the same insert, scan, delete, cursor-delete, and cursor-restart pattern as `mtest.c`.

## Control flow
The program generates random values, prepares a fixed 32-byte key, creates an environment, sets max readers and map size, installs encryption before open, inserts random string records with `MDB_NOOVERWRITE`, scans, deletes selected records, scans again, deletes through a cursor, and verifies cursor behavior in and after the write transaction.

## State and persistence behavior
It writes encrypted pages to `./testdb`. The key is static and embedded in the executable. All data persistence depends on the encryption callback producing reversible page transformations compatible with LMDB's page handling.

## Dependencies and integration points
The test includes `chacha8.h` and depends on LMDB's direct encryption callback API. It validates that normal B-tree operations work with encrypted pages.

## Risks and edge cases
The static key is not secure for real use. The delete stride can be zero. Using a custom encryption function without authentication means corruption detection depends on other checks. As with `mtest.c`, string buffer key sizing is unusual.

## Test signals
Successful completion, readable decrypted cursor output, duplicate skips, post-delete scans, and clean close verify encrypted basic operations.
