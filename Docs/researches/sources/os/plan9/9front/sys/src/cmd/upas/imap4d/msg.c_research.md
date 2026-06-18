# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/msg.c

Implements message loading, MIME/header parsing, RFC822 address parsing, body sizing, and memory cleanup for IMAP messages.

Key responsibilities:
- Lazily reads upas/fs `info`, `rawheader`, `mimeheader`, `rawbody`, and child part directories.
- Normalizes headers to CRLF and caches them with size/line counts.
- Parses MIME headers into `Mimehdr` chains.
- Parses RFC822 address headers into `Maddr` lists.
- Builds MIME/message child trees from upas/fs part directories.
- Computes raw body sizes adjusted for missing CR before LF, matching IMAP octet semantics.
- Selects header fields for partial body fetch/search.

Important functions:
- `msgreadfile()` reads a named file from a message directory.
- `msginfo()` parses fixed upas/fs `info` fields.
- `msgstruct()` constructs message/MIME tree and handles `message/rfc822` nesting.
- `msgbodysize()` counts raw body bytes and line count with CRLF correction.
- `msgheader()` reads and normalizes headers, then parses content and address fields.
- `selectfields()` emits selected header fields for `BODY[HEADER.FIELDS...]`.
- `headaddress()`, `headaddrspec()`, `headdomain()`, and related helpers implement a permissive RFC822-ish address parser.
- `freemsg()` recursively frees message state.

Filesystem relevance:
- Message files are opened relative to `m->fsdir` and `m->fs`.
- Subparts are modeled by appending path components under upas/fs message directories.
- `msgdead()` checks whether a message path still exists and marks it expunged.

Notable risks and quirks:
- Parser intentionally extends address syntax to handle `!` and local names.
- Several comments call out “BOTCH” around `message/rfc822` path manipulation and upas/fs behavior.
- Header parser tolerates 8-bit characters in atoms for UTF data.
- `mimelanguage()` loops while `headchar(0) != ','`, which can run through line ends via `headchar(1)` behavior; malformed headers rely on parser termination.
