# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/pscrypt.c

Adobe Type 1 eexec/CharString encryption and decryption tool.

Key responsibilities:
- Implements the Adobe cipher with seeds for eexec and show/CharString.
- Supports encrypt and decrypt modes.
- Reads hex or binary input and writes hex or binary output.
- Injects an encryption key for encrypt mode or strips initial decrypted key bytes for decrypt mode.
- Supports custom seed and hex line length.

Important behavior:
- Default decrypt mode expects hex input and binary output, omitting the first four output bytes.
- Default encrypt mode expects binary input and hex output, prepending four key bytes.
- Cipher update uses constants `MAGIC1=52845` and `MAGIC2=22719`.

Notable risks:
- `nexthexchar()` does not robustly handle odd or truncated hex input before combining nibbles.
- Global `lastchar` controls loop termination across multiple input files.
