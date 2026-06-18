# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/print.c

Defines custom formatters used by IMAP command handlers.

Key responsibilities:
- `Ffmt`: formats mailbox paths as quoted `/mail/box/<user>/...` paths unless already `/imap` or `/pop`.
- `Zfmt`: formats IMAP strings, choosing quoted strings, literals, `NIL`, or empty quoted strings; `%Y` additionally decodes fs names and encodes modified UTF-7.
- `Xfmt`: decodes modified UTF-7, cleans path names, and encodes filesystem names.
- `Dfmt`: formats RFC822-style dates or IMAP internal dates, using `%δ` as non-quoted date output.

Filesystem relevance:
- Central to safe mailbox-path display and conversion between IMAP mailbox names and filesystem encodings.

Notable constraints:
- Literal output is used for strings requiring non-ASCII/control handling unless alternate formatting rejects them.
- `%#Z` alternate avoids quoting if possible and logs bad literal cases.
