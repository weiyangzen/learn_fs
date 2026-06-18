# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherrc4.c

SSH2 RC4/arcfour cipher adapter.

Key responsibilities:
- Initializes RC4 state from negotiated directional key.
- Provides stream encrypt/decrypt callbacks using the same RC4 operation.
- Exports `Cipher cipherrc4` named `arcfour`.

Risks/quirks:
- RC4/arcfour is legacy and cryptographically weak.
- Declares block size as 8 in `Cipher`, likely fitting surrounding packet code expectations.
