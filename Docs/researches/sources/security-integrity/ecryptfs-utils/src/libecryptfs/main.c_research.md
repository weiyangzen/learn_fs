# sources/security-integrity/ecryptfs-utils/src/libecryptfs/main.c

## Purpose
Core utility routines for libecryptfs: version reporting, hex conversion, NSS hashing, private mount discovery, mount-state checks, passphrase signature and auth-token payload generation, private-key payload generation, and zombie session placeholder tracking with System V IPC.

## Important APIs, types, and functions
- `ecryptfs_get_versions`, `to_hex`, `from_hex`, and `do_hash` provide foundational helpers.
- `ecryptfs_fetch_private_mnt` reads `~/.ecryptfs/Private.mnt` or falls back to `$HOME/Private`.
- `ecryptfs_private_is_mounted` scans `/proc/mounts` for eCryptfs device/mount/signature matches.
- `generate_passphrase_sig` performs salted iterative SHA-512 hashing, yields FEKEK bytes and expanded-hex signature.
- `generate_payload` fills password auth-token fields; `ecryptfs_generate_key_payload` fills private-key auth-token fields from a key module.
- Zombie placeholder functions manage session-id to pid pairs in shared memory guarded by a semaphore.

## Control flow
Passphrase signature generation concatenates salt and passphrase, hashes with NSS SHA-512 for `ECRYPTFS_DEFAULT_NUM_HASH_ITERATIONS`, copies the first key bytes as FEKEK, hashes once more, and hex-encodes the signature. Private-key payload generation asks the module for blob and key-data sizes, copies or generates blob data, derives or requests a signature, and fills auth-token metadata. Zombie placeholder setup locks IPC state, appends the current session/pid pair, sleeps, then removes the pair and exits; clear logic finds the pid for the current session, kills it, and removes the entry.

## State and persistence behavior
Reads `/proc/mounts`, user mount config files, and System V shared memory/semaphores keyed by eCryptfs constants. Auth-token helpers mutate caller-provided memory only. Zombie helpers create shared IPC objects and can send `SIGKILL` to tracked processes.

## Dependencies and integration points
Used by `key_management.c`, mount helpers, PAM workflows, and private directory helpers. Depends on NSS hashing, Linux mount table APIs, key-module callbacks, signals, and System V IPC.

## Risks and edge cases
The passphrase KDF is a fixed legacy iterative SHA-512 scheme, not a modern memory-hard KDF. Several mount-path helpers allocate strings with ownership handed to callers but can leak on early errors. `ecryptfs_private_is_mounted` deliberately uses broad matching when mounting and strict matching when unmounting, so callers must pass correct `mounting` intent. Zombie shared-memory code assumes `sizeof(pid_t) == sizeof(uint32_t)` and contains manual byte-order and buffer-shift logic that is easy to break.

## Test signals
Tests should compare known passphrase/salt signature vectors, verify auth-token field layout, mock mount table entries for mount/unmount matching, exercise private mount fallback behavior, and run IPC placeholder add/find/remove operations in an isolated namespace or with cleanup.
