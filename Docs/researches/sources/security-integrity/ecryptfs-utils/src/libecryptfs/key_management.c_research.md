# sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_management.c

## Purpose
Implements passphrase and key-module authentication-token lifecycle operations: generating auth-token payloads, adding/removing keys in the Linux user keyring, wrapping and unwrapping passphrase files, reading salt/signature caches, terminal passphrase prompting, and locating the default wrapped-passphrase file.

## Important APIs, types, and functions
- `ecryptfs_generate_passphrase_auth_tok`, `ecryptfs_passphrase_blob`, and `ecryptfs_passphrase_sig_from_blob` generate and expose password auth-token data.
- `ecryptfs_add_auth_tok_to_keyring`, `ecryptfs_add_blob_to_keyring`, `ecryptfs_add_passphrase_key_to_keyring`, and `ecryptfs_remove_auth_tok_from_keyring` integrate with keyutils.
- `ecryptfs_wrap_passphrase`, `ecryptfs_wrap_passphrase_file`, and `ecryptfs_unwrap_passphrase` manage wrapped-passphrase files with NSS AES-ECB.
- `ecryptfs_insert_wrapped_passphrase_into_keyring` inserts both FNEK and normal passphrase keys.
- `ecryptfs_add_key_module_key_to_keyring` builds private-key auth-token payloads from key modules.
- `ecryptfs_read_salt_hex_from_rc`, `ecryptfs_check_sig`, `ecryptfs_append_sig`, `ecryptfs_get_passphrase`, and `ecryptfs_get_wrapped_passphrase_filename` support user configuration and prompting.

## Control flow
Passphrase insertion derives a FEKEK/signature, fills an auth token, searches the user keyring for an existing key, and adds it if absent. Wrapping validates passphrase length, derives a wrapping key, pads to AES block size, encrypts with NSS, writes signature plus ciphertext to a newly created `0600` file, and removes the plaintext source in the file wrapper path. Unwrapping derives the same signature, verifies the file prefix, decrypts the remainder, and leaves the plaintext in the caller buffer. Key-module insertion queries blob size, allocates an auth token with appended blob storage, generates payload/signature, and adds it to the keyring.

## State and persistence behavior
Mutates the Linux user keyring and signature cache files. Wrapped-passphrase operations create, unlink, or replace files in the user's eCryptfs directory. Sensitive buffers are sometimes zeroed before free, but many stack buffers, NSS temporaries, Python-facing blobs, and passphrase strings are not comprehensively wiped.

## Dependencies and integration points
Depends on NSS/PKCS#11, keyutils, passwd database, termios, rc-file parsing, and core payload helpers in `main.c`. It is used by mount helpers, PAM support, SWIG bindings, decision-graph key-module subgraphs, and miscdev packet processing.

## Risks and edge cases
AES-ECB for passphrase wrapping is legacy and exposes structure for repeated blocks. Some error paths call `close(fd)` after failed `open`, use positive `errno` conventions inconsistently, or leave allocated data uncleared. `ecryptfs_insert_wrapped_passphrase_into_keyring` writes into the same `auth_tok_sig` buffer for two salts, so callers must know the final signature semantics. `ecryptfs_get_wrapped_passphrase_filename` returns `NULL` if `stat` fails instead of returning the default path for creation.

## Test signals
Integration tests require keyutils and NSS availability. Useful coverage includes deterministic signature generation, keyring add/search/remove idempotence, wrap/unwrap round trips, wrong wrapping passphrase rejection, rc-file salt parsing, signature cache append/check behavior, passphrase length enforcement, and keyring quota failure handling.
