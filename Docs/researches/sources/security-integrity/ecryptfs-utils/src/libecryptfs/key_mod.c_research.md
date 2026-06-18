# sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_mod.c

## Purpose
Discovers, registers, and frees eCryptfs key modules. It provides fallback dummy operations for optional module methods, includes the built-in passphrase module, and supports dynamically loaded `.so` modules from the configured key-module directory.

## Important APIs, types, and functions
- `builtin_get_key_mod_ops` currently registers `passphrase_get_key_mod_ops`.
- `ecryptfs_fill_in_dummy_ops` supplies no-op or warning implementations for missing `struct ecryptfs_key_mod_ops` callbacks.
- `ecryptfs_register_key_modules` loads dynamic modules with `dlopen`/`dlsym("get_key_mod_ops")`, initializes aliases, then appends built-ins not shadowed by dynamic modules.
- `ecryptfs_find_key_mod` searches the registered list.
- `ecryptfs_free_key_mod_list` finalizes modules, closes dynamic handles, and frees module records.
- `ecryptfs_generate_sig_from_key_data` is a placeholder that currently rejects all key-data types.

## Control flow
Registration opens `ECRYPTFS_DEFAULT_KEY_MOD_DIR`, scans for filenames ending in `.so`, loads each library lazily, resolves its ops factory, fills missing callbacks, calls `init` for the alias, and appends it to `ctx->key_mod_list_head`. It then iterates built-in factories and skips a built-in if a dynamic module with the same alias already exists. Lookup is a linear alias prefix comparison.

## State and persistence behavior
Maintains an in-memory linked list hanging off `struct ecryptfs_ctx`. Dynamic library handles stay open until `ecryptfs_free_key_mod_list`. No persistent files are written; discovery reads the key-module directory.

## Dependencies and integration points
Used by `module_mgr.c` to build key selection graphs, by `packets.c` to locate modules for encrypt/decrypt requests, and by `key_management.c` to generate key-module auth-token payloads. Depends on libdl, directory iteration, and key-module ABI contracts in `ecryptfs.h`.

## Risks and edge cases
Failure to open the dynamic module directory returns `-EPERM`, which can block even built-in module registration. `ecryptfs_find_key_mod` uses `strncmp` with the registered alias length, so prefix matches can accidentally select a module. `ecryptfs_free_key_mod_list` calls `dlclose` even for built-ins with a null handle. Dummy cryptographic operations can mask incomplete modules until runtime behavior fails.

## Test signals
Tests should exercise registration with missing module directory, a fake dynamic module, dynamic-over-built-in alias precedence, missing optional callbacks, lookup prefix collisions, and cleanup of mixed dynamic/built-in lists. Packet and decision-graph integration tests should confirm the passphrase module is always available in normal builds.
