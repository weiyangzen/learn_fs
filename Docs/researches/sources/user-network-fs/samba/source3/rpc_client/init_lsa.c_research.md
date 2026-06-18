# sources/user-network-fs/samba/source3/rpc_client/init_lsa.c

## Purpose
`init_lsa.c` provides small initializers for LSA string structures and builders for encrypted trusted-domain authentication blobs used by LSA RPC calls. It prepares both legacy RC4 and newer AES-protected trust domain password payloads.

## Important APIs, Types, And Functions
String helpers are `init_lsa_String()`, `init_lsa_StringLarge()`, `init_lsa_AsciiString()`, and `init_lsa_AsciiStringLarge()`. Trust helpers are `rpc_lsa_encrypt_trustdom_info()` and `rpc_lsa_encrypt_trustdom_info_aes()`. They populate `trustDomainPasswords`, `AuthenticationInformation`, `lsa_TrustDomainInfoAuthInfoInternal`, and `lsa_TrustDomainInfoAuthInfoInternalAES` structures.

## Control Flow
String helpers assign pointers and, for `lsa_String`, set byte length and size from `strlen_m()`. The RC4 trust flow converts old/new incoming/outgoing cleartext passwords from Unix charset to UTF-16, stamps all four auth entries with the current NT time, fills a confounder, NDR-marshals `trustDomainPasswords`, then encrypts the resulting blob with ARCFOUR using the session key. The AES flow builds the same plaintext, generates a salt, and calls `samba_gnutls_aead_aes_256_cbc_hmac_sha512_encrypt()` with LSA-specific encryption and MAC salts, storing ciphertext and auth data.

## State And Persistence
The file persists no global state. It allocates returned blobs under caller-provided talloc contexts and uses current time plus random confounder/salt values, so output is intentionally non-deterministic. Password buffers remain in talloc allocations used for the marshalled/encrypted blobs.

## Dependencies And Integration Points
Dependencies include generated LSA and DRS blob NDR, `dcerpc_lsa.h`, Samba charset conversion, random buffer helpers, GnuTLS cipher APIs, and Samba AEAD helper salts. Callers include `rpcclient/cmd_lsarpc.c` and LSA RPC torture tests for trusted domain password operations.

## Risks
The functions return `bool`, so detailed conversion, NDR, or crypto failures are collapsed. The RC4 helper calls `gnutls_cipher_init()` and encrypt without checking their return codes. Password inputs are expected non-NULL and are measured with `strlen()`. The AES helper rejects ciphertext shorter than 520 bytes, a protocol-shape assumption that should be preserved by tests.

## Test Signals
Relevant signals are LSA torture tests around trusted domain auth info, rpcclient trust password commands, invalid/null password input coverage, RC4/AES round-trip decryption compatibility, and tests verifying generated blobs have current/previous incoming/outgoing entries with expected timestamps and auth types.
