# sources/storage-engines/lmdb/libraries/liblmdb/module.c

## Purpose
`module.c` provides helper routines for dynamically loading LMDB crypto modules and applying their checksum/encryption hooks to an environment.

## Important APIs, types, and functions
`mdb_modload` loads a shared library and resolves a hook function, defaulting to symbol `MDB_crypto`, then stores the returned `MDB_crypto_funcs`. `mdb_modunload` releases the platform module handle. `mdb_modsetup` installs checksum and encryption callbacks with `mdb_env_set_checksum` and `mdb_env_set_encrypt`, deriving an encryption key from a password when possible.

## Control flow
The implementation branches between Windows `LoadLibrary`/`GetProcAddress`/`FreeLibrary` and POSIX `dlopen`/`dlsym`/`dlclose`. On load failure or missing hook symbol, it sets an error message and releases any partial handle. Setup installs checksum hooks first; if an encryption function and password are provided, it fills a stack key buffer either through `mcf_str2key` or by copying the password, then zeroes the key buffer after configuring the environment.

## State and persistence behavior
The file mutates LMDB environment configuration before `mdb_env_open`. It does not persist data itself, but its hooks determine on-disk encryption, checksum size, and page validation behavior.

## Dependencies and integration points
LMDB utilities and encrypted tests call these helpers. Runtime modules must expose an `MDB_crypto_hooks` function returning `MDB_crypto_funcs`.

## Risks and edge cases
`keybuf` is fixed at 2048 bytes and assumes module key sizes fit. `strncpy` does not guarantee null termination, but the key is binary and sized by `mcf_keysize`. If no password is provided, encryption hooks are not installed even when the module supports encryption. Error messages are static on Windows and less diagnostic than POSIX `dlerror`.

## Test signals
Tests should cover successful module load/unload, missing shared library, missing hook symbol, checksum-only modules, encryption modules with password derivation, oversized key sizes, and cross-platform loader behavior.
