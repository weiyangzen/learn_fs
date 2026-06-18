# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mutf7.c

Implements IMAP modified UTF-7 encoding and decoding for mailbox names.

Key behavior:
- `initm64` builds the modified base64 alphabet, using `,` instead of `/`.
- `encmutf7` copies printable ASCII directly, encodes non-ASCII/control runs as `&...-`, and encodes literal `&` as `&-`.
- `decmutf7` reverses this format, validating alphabet entries and zero padding bits.

Integration points:
- Used by mailbox list/command parsing helpers for IMAP mailbox name transport.
- Uses Plan 9 rune conversion functions `chartorune`, `runetochar`, and `runelen`.

Risks and notes:
- Enforces output limits and returns `-1` on malformed input or insufficient buffer.
- Encoding intentionally does not allow escaped printable ASCII except `&`, matching IMAP modified UTF-7 behavior.
