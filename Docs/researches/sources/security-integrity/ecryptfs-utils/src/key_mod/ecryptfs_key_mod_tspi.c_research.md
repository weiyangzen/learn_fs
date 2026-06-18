# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_tspi.c

Purpose: TrouSerS/TPM key module that seals/unseals eCryptfs session keys using TPM-stored keys identified by UUID.

Important APIs/functions: UUID serialization/deserialization and parsing, TPM public-key signature generation, `ecryptfs_tspi_get_key_sig`, connection ticket pool (`grab_ticket`/`release_ticket`), `ecryptfs_tspi_encrypt`, `ecryptfs_tspi_decrypt`, parameter handling for `tspi_uuid`, `ecryptfs_tspi_init/get_params/get_blob/destroy/finalize`, and `get_key_mod_ops()`.

Control flow: init builds a free list of up to 10 connection tickets. Blob generation converts a hex UUID string into `TSS_UUID`. Encryption/decryption deserialize UUID, grab a connected TSS context ticket, load the SRK with the well-known secret, load the user key by UUID, and seal/unseal data. Decrypt caches loaded key handles in a global UUID mapper. Finalize waits briefly for used tickets, closes initialized contexts, and reports busy if tickets remain.

State/persistence: persistent TPM keys live in TrouSerS persistent storage. Runtime state includes ticket lists/counters, connected TSS contexts, cached key handles, static SRK handles/policies, and serialized UUID blobs.

Dependencies/integration: TrouSerS TSS APIs, pthread mutexes, OpenSSL SHA1, ecryptfs key module ops.

Risks: ticket list manipulation appears to assume simple head movement and may mishandle non-head used tickets. Global encrypt/decrypt locks serialize operations. SRK well-known secret is assumed. Error paths may leak TSS objects or allocated mapper entries.

Test signals: requires TPM/TrouSerS environment; build with `--enable-tspi`, UUID parameter parsing, signature generation, and seal/unseal integration.
