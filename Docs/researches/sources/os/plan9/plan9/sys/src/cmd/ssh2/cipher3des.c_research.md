# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipher3des.c

SSH2 3DES-CBC cipher adapter.

Key responsibilities:
- Initializes `DES3state` from negotiated server-to-client or client-to-server keys and IVs.
- Provides CBC encrypt/decrypt callbacks.
- Exports `Cipher cipher3des` named `3des-cbc` with 8-byte block size.

Dependencies:
- Uses `netssh.h` connection fields `s2cek`, `c2sek`, `s2civ`, and `c2siv`.
- Allocates with `emalloc9p`.

Risks/quirks:
- Legacy cipher retained for protocol compatibility.
