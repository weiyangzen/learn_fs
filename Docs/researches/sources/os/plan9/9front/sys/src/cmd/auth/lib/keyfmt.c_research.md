# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/keyfmt.c

Formatter for DES keys in traditional octal presentation.

Key responsibilities:
- Converts 7-byte DES key material into 8 bytes with parity bits cleared.
- Formats the resulting bytes as eight three-digit octal values.
- Installs as a `Fmt` formatter, commonly `%K`.

Dependencies:
- Used by netkey/key printing tools.
