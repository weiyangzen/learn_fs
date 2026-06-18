# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc2.c

## Purpose
`mtest_enc2.c` tests encrypted LMDB operation through a dynamically loaded crypto module rather than an in-process encryption callback.

## Important APIs, types, and functions
It calls `mdb_modload("./crypto.lm", NULL, &mcf, &errmsg)`, `mdb_modsetup(env, mcf, password)`, and `mdb_modunload`. The remaining database workflow mirrors `mtest_enc.c`: environment setup, writes with `mdb_put`, cursor scans, deletes, and cursor restart checks.

## Control flow
After generating random values, the program creates an environment, loads `crypto.lm`, applies crypto functions using a passphrase, sets reader/map parameters, opens the DB, inserts records, scans, deletes selected keys, performs cursor deletion and restart checks, then closes DBI/env and unloads the module.

## State and persistence behavior
It writes encrypted data to `./testdb` using the crypto module's checksum/encryption configuration. The passphrase and module behavior define persistent compatibility; future opens must use the same module/key derivation.

## Dependencies and integration points
The file integrates `module.c`'s dynamic-loader API with the standard LMDB C API and requires a built `crypto.lm` in the working directory.

## Risks and edge cases
If `crypto.lm` is missing or exports the wrong hook, the program exits early. The passphrase is hardcoded. Random delete stride can be zero. It does not unload the module on failures after loading unless reaching the normal close path.

## Test signals
This test should be run with a known crypto module, verifying successful module load, encrypted write/read/delete behavior, and clean module unload. Negative tests for missing module and wrong password are also useful.
