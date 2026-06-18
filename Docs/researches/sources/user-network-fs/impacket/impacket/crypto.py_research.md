# sources/user-network-fs/impacket/impacket/crypto.py

## Purpose

`crypto.py` implements several cryptographic helpers used by Windows protocols in Impacket: AES-CMAC and AES-CMAC-PRF-128, NIST SP 800-108 counter-mode KDF with HMAC-SHA256, LSA secret encryption/decryption helpers, and SAM NTLM hash DES wrapping helpers.

## Important APIs, Types, and Functions

Core AES-CMAC helpers are `Generate_Subkey`, `XOR_128`, `PAD`, `AES_CMAC`, and `AES_CMAC_PRF_128`. `KDF_CounterMode` derives key material using HMAC-SHA256 with label/context formatting. `LSA_SECRET_XP` models the decrypted LSA secret blob. DES-related helpers are `transformKey`, `decryptSecret`, `encryptSecret`, `SamDecryptNTLMHash`, and `SamEncryptNTLMHash`.

## Control Flow

At import time the module tries to import `DES` and `AES` from `Cryptodome.Cipher`; on failure it logs warnings but does not stop import. `Generate_Subkey` encrypts the all-zero block with AES-ECB, shifts the result as a 128-bit value, and applies the CMAC Rb constant. `AES_CMAC` slices input to the provided length, determines whether the last block is complete, XORs the last block with K1 or padded data with K2, and encrypts the CBC-MAC chain with AES-ECB. `AES_CMAC_PRF_128` first normalizes non-16-byte variable keys by CMACing them under a zero key.

`KDF_CounterMode` iterates counters, HMACs `counter || Label || 0x00 || Context || L`, and returns the requested number of bits truncated to bytes. LSA/SAM helpers transform 7-byte keys into DES keys, then decrypt or encrypt 8-byte blocks. LSA secret helpers rotate through key material in 7-byte chunks and parse or build the `LSA_SECRET_XP` wrapper.

## State and Persistence Behavior

The module is stateless aside from imported cipher classes and logging. All functions operate on caller-provided bytes and return derived bytes. There is no secure memory clearing, no caching, and no file persistence.

## Dependencies and Integration Points

It depends on `pycryptodomex` (`Cryptodome.Cipher.DES` and `AES`), `struct`, `hmac`, `hashlib`, `six.b`, `impacket.structure.Structure`, and package `LOG`. The algorithms are protocol support for LSAD, SAMR, SMB authentication, and other Windows secret/key derivation paths.

## Risks and Edge Cases

If `Cryptodome` is unavailable, import succeeds but crypto functions will fail later with missing names. `AES_CMAC` trusts the separate `length` argument and truncates `M` accordingly. `KDF_CounterMode` calculates `n = L // 256` and only rounds zero to one, so non-multiple-of-256 bit lengths beyond the first block are under-derived instead of using ceiling division. `encryptSecret` prints `tmpStrKey` type and value, leaking key material to stdout. DES helpers require correctly sized inputs and do not validate lengths. These primitives are security-sensitive and should be tested against external vectors.

## Test Signals

Tests should use RFC 4493 AES-CMAC vectors, RFC 4615 PRF vectors, SP 800-108 counter-mode vectors including non-256-bit output lengths, known SAM hash wrapping vectors, and LSA secret round-trips. Environment tests should assert clear failure behavior when `pycryptodomex` is missing and ensure no secret material is printed during encryption.
