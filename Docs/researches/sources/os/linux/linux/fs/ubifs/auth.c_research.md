# File Research: sources/os/linux/linux/fs/ubifs/auth.c

Purpose: UBIFS authentication helpers: node hashing, HMAC generation/verification, superblock PKCS#7 signature verification, key setup, and authentication teardown.

Key APIs:
- `__ubifs_node_calc_hash`, `__ubifs_node_check_hash`, `ubifs_bad_hash`
- `ubifs_prepare_auth_node`
- `ubifs_sb_verify_signature`
- `ubifs_init_authentication`, `__ubifs_exit_authentication`
- `__ubifs_node_insert_hmac`, `__ubifs_node_verify_hmac`
- `__ubifs_shash_copy_state`
- `ubifs_hmac_wkm`, `ubifs_hmac_zero`

Implementation notes:
- Node hashes use `c->hash_tfm` over common header length.
- Authentication nodes store an HMAC over the running hash state.
- HMAC excludes common node magic/CRC and excludes the embedded HMAC field itself.
- `ubifs_init_authentication()` resolves hash algorithm name, requests a logon key, allocates hash and HMAC shash transforms, validates digest sizes, sets HMAC key from key payload, marks filesystem authenticated, and initializes `c->log_hash`.
- Superblock signature verification scans after the superblock node for `UBIFS_SIG_NODE`, checks type `UBIFS_SIGNATURE_TYPE_PKCS7`, then calls `verify_pkcs7_signature`.

Security/correctness:
- HMAC compare uses `crypto_memneq`.
- Revoked or wrong-type keys are rejected.
- Oversized hash/HMAC algorithms are rejected against UBIFS fixed arrays.
- On init failure, allocated crypto transforms are freed and key semaphore/reference is released.
