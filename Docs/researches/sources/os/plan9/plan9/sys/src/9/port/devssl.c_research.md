# File Research: sources/os/plan9/plan9/sys/src/9/port/devssl.c

Purpose: Legacy SSL-style record-layer device `#D/ssl`. It wraps an existing fd, exposes per-conversation `ctl`, `data`, `secretin`, `secretout`, `encalgs`, and `hashalgs`, and applies SSL record framing, optional digesting, and optional encryption.

Key structures:
- `Dstate`: connection state, underlying channel, input/output `OneWay` crypto state, record buffers, owner, and permissions.
- `OneWay`: secret, message id, encryption/hash state, and locks.

Key logic:
- Clone/open creates up to 512 digest/encryption states.
- `ctl` commands set `fd`, configure `alg`, or set base64 secrets.
- `secretin`/`secretout` write raw secrets.
- `data` reads parse SSLv2-like record headers, decrypt, verify digest, remove padding, and return plaintext.
- `data` writes split data into SSL records, add digest and padding, encrypt, and write to the underlying channel.
- Supports clear, digest-only, encryption-only, and digest-plus-encryption modes.

Dependencies and integration:
- Uses `libsec` MD4/MD5/SHA1, DES, RC4, Plan 9 block I/O, and channel wrapping via `fdtochan`.

Risks and notes:
- Cryptography is obsolete: DES, RC4, MD4/MD5/SHA1, including 40-bit variants.
- `NOSPOOKS` enables broader algorithm list.
- Interrupts during writes can desynchronize the remote record stream.
- This is older than `devtls.c` and implements SSL framing rather than modern TLS semantics.
