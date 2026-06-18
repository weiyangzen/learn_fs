# File Research: sources/os/linux/linux-stable/fs/ubifs/auth.c

Purpose: Implements UBIFS authentication helpers for node hashes, HMACs, superblock signature verification, authentication initialization, and cleanup.

Key responsibilities:
- Calculates and checks node hashes.
- Builds authentication nodes by finalizing a running hash state and storing an HMAC.
- Reports hash mismatches with expected and calculated digests.
- Verifies signed superblocks using a following `UBIFS_SIG_NODE` and PKCS#7 verification.
- Initializes authentication from mount-selected hash and logon key, allocating hash and HMAC transforms.
- Manages the log hash descriptor and frees authentication resources.
- Inserts and verifies embedded node HMACs while excluding magic/CRC and the HMAC field itself.
- Copies shash state by export/import.
- Computes a HMAC over the well-known `"UBIFS"` message and tests all-zero HMACs.

Important interactions:
- Uses Linux crypto shash APIs, keyring logon keys, PKCS#7 verification, and UBIFS scan/read helpers.
- Authentication fields live in `struct ubifs_info` and are gated by `ubifs_authenticated(c)`.

Notable invariants and risks:
- Hash and HMAC digest sizes must fit fixed UBIFS on-media arrays.
- The authentication key must be a logon key and can be revoked while being requested, so key semaphore checks matter.
- HMAC verification uses constant-time comparison semantics via `crypto_memneq()`.
