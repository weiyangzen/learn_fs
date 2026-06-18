# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mutf7.c

Implements IMAP modified UTF-7 mailbox-name encoding and decoding.

Key responsibilities:
- Builds modified base64 tables using `,` instead of `/`.
- `encmutf7()` encodes non-ASCII/control runs as `&...-` and special-cases `&` as `&-`.
- `decmutf7()` decodes `&...-` runs back to UTF-8 Runes and validates trailing unused bits.

Filesystem relevance:
- Used by IMAP `LIST`/`LSUB` formatting and mailbox-name parsing to bridge client mailbox names and local filesystem names.

Notable constraints:
- Comment states it is not compatible with characters outside the Unicode basic plane.
- Decoder rejects literal control/non-ASCII bytes outside encoded sections.
