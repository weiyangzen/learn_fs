# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devssl.c

Implements old Plan 9 `#D/ssl`, a record wrapper providing SSL-style framing, optional digesting, and optional encryption over an existing channel.

Key behavior:
- Exposes `ssl`, `clone`, per-connection directories, `ctl`, `data`, `secretin`, `secretout`, `encalgs`, and `hashalgs`.
- Creates up to 128 `Dstate` records.
- `ctl` accepts an fd binding and algorithm configuration.
- Secrets are written directly or base64-decoded through control commands.
- Supports clear, digest-only, encryption-only, or digest+encryption states.
- Implements SSL-style record headers with optional padding.
- Maintains independent input/output secrets, crypto states, and message sequence IDs.
- Reads parse records, decrypt, verify digest, remove padding, and return application data.
- Writes split data into records, add digest, add padding, encrypt, and write to the wrapped channel.

Algorithms:
- Hashes: MD4, MD5, SHA1/SHA.
- Encryption: DES CBC/ECB and RC4 variants, including 40-bit compatibility variants.

Notable risks:
- This is legacy SSL-style crypto, not modern TLS.
- It permits weak algorithms by design.
- It explicitly refuses to wrap another `#D/ssl` file.
