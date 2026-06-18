# File Research: sources/os/bsd/freebsd-src/sbin/decryptcore/decryptcore.c

## Purpose
Decrypts encrypted FreeBSD kernel core dumps using a private RSA key and kernel dump key file.

## Main Elements
- `usage()`: supports explicit key/core paths or crashdir plus dump number.
- `read_key()`: reads `struct kerneldumpkey`, converts encrypted-key size from dump endian, and reads appended encrypted key bytes.
- `decrypt()`: forks a child, opens inputs, enters Capsicum capability mode, reads RSA private key, decrypts dump key with OAEP or legacy PKCS#1 padding, initializes AES-256-CBC or ChaCha20 EVP decryption, streams plaintext to output, and exits with status.
- `main()`: parses options, derives `/var/crash/key.N`, `vmcore.N`, and `vmcore_encrypted.N` names when `-n` is used, handles `-f`, creates output with `O_EXCL`, deletes partial output on failure, and manages logging mode.

## Dependencies And Integration
Uses kernel dump metadata from `<sys/kerneldump.h>`, OpenSSL EVP/RSA/PEM APIs, Capsicum helpers, and `pjdlog`.

## Risk Notes
The parent unlinks partially decrypted output on child failure. Private-key and encrypted-core processing happens after entering capability mode, limiting filesystem reach after descriptors are open.
