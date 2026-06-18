# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.h

This header defines IKE crypto transform types, key state, block helpers, and crypto APIs.

Key contents:
- Includes OpenSSL DES, CAST, AES, and OpenBSD Blowfish types.
- Defines XOR/copy macros for 64-bit block operations, currently using the 32-bit implementation path.
- Defines big-endian 32-bit set/get macros.
- Defines `BLOCKSIZE` as 8 and `MAXBLK` as `AES_BLOCK_SIZE`.
- `struct keystate`: transform back pointer, IV buffers, active IV pointers, and cipher key schedule union.
- Cipher key schedule aliases: `ks_des`, `ks_blf`, `ks_cast`, `ks_aes`.
- `enum transform`: Oakley transform IDs for DES, IDEA, Blowfish, RC5, 3DES, CAST, AES.
- `enum cryptoerr`: crypto initialization error codes.
- `struct crypto_xf`: transform descriptor with ID, name, key range, block size, optional state pointer, and function pointers.
- Prototypes for transform lookup, initialization, IV management, encryption/decryption, and state cloning.

Research notes:
- The header exposes a generic transform interface used by exchange/keying code.
