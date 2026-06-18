# File Research: sources/os/plan9/9front/sys/src/cmd/upas/marshal/marshal.c

Implements `upas/marshal`, the outbound mail message assembler and sendmail front-end.

Key responsibilities:
- Parses command-line recipients, CC/BCC, subject, content type, attachments/includes, PGP options, save-to folder, reply message path, and sendmail flags.
- Reads and normalizes user-supplied headers from stdin, optionally extracting recipients from RFC822 headers with `-8`.
- Expands user aliases from the `names` mailbox file.
- Adds missing headers such as `Date`, `From`, `To`, `Cc`, `Subject`, `In-Reply-To`, and `MIME-Version`.
- Detects body content transfer encoding as `US-ASCII`/`UTF-8` and builds multipart MIME output for attachments.
- Optionally filters the body through `/bin/pgp`.
- Starts sendmail, optionally tees the outgoing message into a local folder.
- Encodes non-ASCII header text with RFC2047 quoted-printable style.

Important functions:
- `main()` orchestrates parsing, header/body processing, attachments, PGP, and subprocess cleanup.
- `readheaders()` coalesces multiline headers, classifies known fields, removes Bcc, expands aliases, and handles `Attach:`/`Include:`.
- `body()` writes message body, ensuring leading newline and adding text content headers.
- `attachment()` copies MIME or emits MIME part headers and base64 encodes non-display attachments.
- `mkattach()` determines attachment type from explicit type, extension, `/sys/lib/mimetype`, or `/bin/file -m`.
- `sendmail()` forks `/bin/upas/send` or local hooks and optionally saves a copy.
- `pgpfilter()` interposes `/bin/pgp`.
- `readaliases()`, `expand()`, `expandline()` implement alias expansion and RFC822-ish address preservation.
- `doublequote()` and `rfc2047fmt()` are custom formatters.

Filesystem relevance:
- Reads user `headers` and `names` files from mailbox paths.
- Saves sent messages with `openfolder()`/`fappendfolder()` paths via common upas helpers.
- Uses attachment paths directly and can include message/rfc822 raw files.

Notable risks and quirks:
- `readheaders()` only recognizes likely headers in strict mode; uncommon headers at the top of a body may terminate header parsing.
- Attachment MIME type detection forks `/bin/file`.
- Alias expansion is recursive up to 32 iterations and de-duplicates by string equality.
- Error paths use `fatal()` to kill sendmail/PGP subprocesses and release any hold.
