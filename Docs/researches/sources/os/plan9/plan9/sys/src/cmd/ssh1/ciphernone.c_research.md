# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphernone.c

SSH1 no-encryption cipher adapter.

Key responsibilities:
- Provides no-op encrypt/decrypt callbacks.
- Returns a non-nil sentinel state.
- Exports `Cipher ciphernone`.

Use:
- Compatibility/debugging cipher, not safe for normal use.

Risks/quirks:
- Deliberately disables confidentiality when negotiated.
