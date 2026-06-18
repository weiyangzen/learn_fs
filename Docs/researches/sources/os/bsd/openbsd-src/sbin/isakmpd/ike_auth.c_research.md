# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.c

IKE phase-1 authentication method implementation for pre-shared keys and RSA signatures.

Main components:
- Static `ike_auth[]` table maps authentication method IDs to SKEYID generation, hash decode, and hash encode functions.
- `ike_auth_get()` returns the method descriptor.
- `ike_auth_get_key()` retrieves PSKs, KeyNote RSA keys, X.509 private keys, dynamic credential keys, or default private keys depending on authentication type and ID.
- `pre_shared_gen_skeyid()` finds the PSK, stores it for policy, and computes SKEYID as PRF(PSK, Ni | Nr).
- `sig_gen_skeyid()` computes signature-mode SKEYID as PRF(Ni | Nr, g^xy).
- `pre_shared_decode_hash()` and `pre_shared_encode_hash()` receive/send HASH payloads.
- `rsa_sig_decode_hash()` locates or validates peer public keys from local cert storage, inbound CERT payloads, optional DNSSEC, or public-key files; decrypts the SIG payload to recover the peer HASH; and stores auth material for policy.
- `rsa_sig_encode_hash()` sends a CERT payload when available, obtains the local private key, computes the IKE auth hash, RSA-private-encrypts it, and adds a SIG payload.
- `ike_auth_hash()` computes HASH_I/HASH_R over DH public values, cookies, SA body, and ID.
- `get_raw_key_from_file()` loads peer RSA public keys from the configured pubkey directory.

Important dependencies:
- PRF/hash layer, exchange nonces/IDs, `ipsec_exch` DH material, cert handlers, KeyNote, X.509, monitor file access, config, and key helpers.

Security-relevant notes:
- Private key file loading checks secrecy for X.509 private keys via `check_file_secrecy_fd()`.
- RSA signing enables blinding before private-key operation.
- For PSK auth, the secret is stored in `exchange->recv_key` for later policy processing.
