# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/ecdsa.c

Factotum ECDSA signing protocol for secp256k1-style private keys.

Key responsibilities:
- Supports client-side signing only; server mode is unimplemented.
- Finds a key/password pair, decrypts a base58-encoded encrypted private key, and derives the public point.
- Signs written message bytes with ECDSA over secp256k1.
- DER-encodes `r` and `s` signature integers for reads.
- Frees mpint and EC private-key material on close.

Dependencies:
- Uses factotum key lookup, base58 decode, SHA-256, AES-CBC, mpint EC routines, and `secp256k1` domain initialization.

Notable risks:
- Password/key validation returns `RpcNeedkey` for bad decrypt/checksum.
- The encrypted-key format is specific: version byte, 32-byte private scalar, checksum, and IV.
