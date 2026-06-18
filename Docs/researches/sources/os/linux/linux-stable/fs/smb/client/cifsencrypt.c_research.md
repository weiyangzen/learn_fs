# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsencrypt.c

Read status: complete.

## Purpose

Implements CIFS/SMB cryptographic helper routines for request signing and NTLM/NTLMv2 authentication response generation.

## Main Responsibilities

- Feed SMB request vectors and iterators into MD5, HMAC-SHA256, or AES-CMAC signing contexts.
- Build and parse NTLMSSP AV-pair target-info blobs.
- Construct NTLMv2 authentication responses, including timestamp, client challenge, SPN AV pair, and session key derivation.
- Generate the NTLM session key ciphertext using RC4 for legacy NTLMSSP paths.
- Release SMB3 encryption/decryption AEAD transform handles.

## Important Functions

- `cifs_sig_step()`, `cifs_sig_iter()`, `cifs_sig_final()`
  - Generic signing data path over `iov_iter`.
  - Chooses MD5, HMAC-SHA256, or AES-CMAC based on `struct cifs_calc_sig_ctx`.

- `__cifs_calc_signature()`
  - Calculates a signature over an SMB request’s kvecs and data iterator.
  - Rejects undersized request data and returns traceable `-EIO` on short iterator processing.

- `build_avpair_blob()`
  - Builds a minimal NTLM target-info blob for non-extended negotiate paths.
  - Defaults missing domain to `WORKGROUP`.

- `find_next_av()`, `find_av_name()`, `find_timestamp()`
  - Safe AV-pair iteration helpers.
  - Extract domain names and server timestamp from the NTLMSSP challenge; falls back to local time when no timestamp exists.

- `calc_ntlmv2_hash()`
  - Computes NTLMv2 hash from password NT hash, uppercase Unicode username, and Unicode domain or server IP.

- `set_auth_key_response()`
  - Replaces the session auth response buffer with a full NTLMv2 response layout.
  - Copies existing target info and appends `NTLMSSP_AV_TARGET_NAME` as `cifs/<hostname>` plus EOL.

- `setup_ntlmv2_rsp()`
  - High-level NTLMv2 response builder.
  - Handles domain auto-discovery, DNS domain extraction, timestamp selection, random client challenge, response HMAC, and session key derivation.
  - Disables NTLMv2 under FIPS mode because it relies on legacy MD4/MD5 primitives.

- `calc_seckey()`
  - Generates a random secondary key, encrypts it with RC4 using the NTLM response key, and stores the clear secondary key as the session key.
  - Disabled under FIPS mode.

- `cifs_crypto_secmech_release()`
  - Frees SMB3 AEAD encryption/decryption transforms on the server object.

## Dependencies

- Uses kernel crypto helpers for MD5, SHA/HMAC, AES-CMAC, AEAD, and ARC4.
- Uses session state from `struct cifs_ses` and server state from `struct TCP_Server_Info`.
- Relies on Unicode conversion helpers from `cifs_unicode.h`.

## Notable Behaviors

- Sensitive buffers are freed with `kfree_sensitive()` or wiped with `memzero_explicit()` where appropriate.
- AV-pair parsing validates alignment and bounds before conversion.
- `setup_ntlmv2_rsp()` serializes updates under `cifs_server_lock()` because it rewrites session authentication material tied to the server.
