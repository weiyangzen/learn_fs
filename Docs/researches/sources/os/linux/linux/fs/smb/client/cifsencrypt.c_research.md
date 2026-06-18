# File Research: sources/os/linux/linux/fs/smb/client/cifsencrypt.c

## Purpose
`cifsencrypt.c` implements NTLM/NTLMv2 authentication hashing, signing digest helpers, NTLMv2 response generation, NTLM session-key encryption, and release of SMB3 encryption crypto transforms.

## Main Responsibilities
- Feeds SMB request vectors and iterators into a selected signature/hash context.
- Builds and parses NTLMSSP AV-pair target-info blobs.
- Computes NTLMv2 hash from password hash, uppercased username, and domain/server name.
- Builds the NTLMv2 client response and session key.
- Generates the NTLM encrypted secondary session key using ARC4.
- Releases AEAD crypto transforms stored on `TCP_Server_Info`.

## Important Functions
- `cifs_sig_step()`: updates MD5, HMAC-SHA256, or AES-CMAC context for one iterator segment.
- `cifs_sig_final()`: finalizes whichever signing algorithm context is active.
- `cifs_sig_iter()`: safely walks an `iov_iter` into the signing context.
- `__cifs_calc_signature()`: signs SMB request kvecs plus request data iterator.
- `build_avpair_blob()`: constructs a minimal NTLM target-info AV blob when extended security did not provide one.
- `find_next_av()`: bounded iterator over NTLMSSP AV pairs.
- `find_av_name()`: extracts Unicode AV names such as NetBIOS/DNS domain into session strings.
- `find_timestamp()`: returns server-provided NTLM timestamp or current NT time.
- `calc_ntlmv2_hash()`: computes `HMAC-MD5(NT hash, UppercaseUser + DomainOrServer)`.
- `CalcNTLMv2_response()`: computes NTLMv2 proof response over server challenge and response blob.
- `set_auth_key_response()`: creates final NTLMv2 response buffer, appending SPN AV pair `cifs/<hostname>` and EOL.
- `setup_ntlmv2_rsp()`: top-level NTLMv2 response/session-key setup.
- `calc_seckey()`: creates random secondary key and encrypts it with ARC4 using the session key.
- `cifs_crypto_secmech_release()`: frees SMB3 AEAD encryption/decryption transforms.

## Authentication Flow
1. Determine or build target-info AV pairs.
2. Resolve domain fields from challenge AV pairs when domain autodetection is enabled.
3. Select timestamp from server AV pair or local time.
4. Generate client challenge randomness.
5. Build response blob with target-info and SPN.
6. Reject NTLMv2 in FIPS mode.
7. Calculate NTLMv2 hash.
8. Calculate NTLMv2 proof response.
9. Derive session key from proof response.

## Validation and Safety Notes
- AV-pair parsing checks bounds and aligned UTF-16 lengths.
- `setup_ntlmv2_rsp()` uses `cifs_server_lock()` around response-buffer mutation.
- Old target-info buffer is freed with `kfree_sensitive()`.
- NTLMv2 and ARC4 key paths are disabled/rejected under FIPS where applicable.
- Temporary session-key material is wiped with `memzero_explicit()` and freed using sensitive-free helpers.

## Dependencies
- Uses kernel crypto helpers for MD5, HMAC-MD5, HMAC-SHA256, AES-CMAC, ARC4, random bytes, and FIPS state.
- Depends on session/server structures from `cifsglob.h` and NTLMSSP wire structures from `ntlmssp.h`.
