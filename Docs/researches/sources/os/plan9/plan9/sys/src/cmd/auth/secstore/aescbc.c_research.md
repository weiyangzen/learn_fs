# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/aescbc.c

Standalone encrypt/decrypt tool for secstore-compatible AES-CBC files. It supports password from console, fd 3 (`-i`), or nvram config (`-n`), and encryption mode (`-e`).

Version 2 format writes header `AES CBC SHA1  2\n`, unpredictable IV, encrypted random first block, AES-CBC ciphertext, and HMAC-SHA1 authentication keyed by MD5 of the AES key. Decryption also supports an older compatibility format with trailing `XXXXXXXXXXXXXXXX`.

Used for emergency decryption/encryption of secstore files outside the network client.
