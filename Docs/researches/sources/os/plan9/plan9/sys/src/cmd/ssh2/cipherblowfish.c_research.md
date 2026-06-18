# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherblowfish.c

SSH2 Blowfish-CBC cipher adapter.

Key responsibilities:
- Initializes Blowfish state from negotiated directional key/IV.
- Provides CBC encrypt/decrypt callbacks.
- Exports `Cipher cipherblowfish` named `blowfish-cbc`.

Notable details:
- Prints key/IV material when `debug > 1`.
- Also prints cipher-state pointer and first bytes before/after decrypt unconditionally in current code.

Risks/quirks:
- Unconditional debug `fprint` in init/decrypt leaks runtime internals and plaintext/ciphertext bytes.
- Blowfish-CBC is legacy compatibility code.
