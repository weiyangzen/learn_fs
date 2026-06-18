# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/msg.c

Implements message metadata loading, MIME/RFC822 header parsing, address parsing, MIME tree construction, bogus-message repair views, message sizing, and selected-header extraction for IMAP responses.

Key behavior:
- `msgFile` resolves files inside an `upas/fs` message directory. For corrupt messages marked `bogus`, it synthesizes fake MIME structure and body parts using temporary files.
- `msgInfo` loads the `info` file and populates indexed fields such as subject, digest, message-id, dates.
- `msgStruct` lazily builds MIME/message child trees, parses `unixheader`, `rawheader`, `mimeheader`, and body size, and constructs a single body child for non-multipart leaves.
- `msgReadFile` reads message files into allocated NUL-terminated buffers, using `dirfstat` for larger files.
- `msgBodySize` counts raw body bytes/lines and adjusts size for bare LF conversion; null bytes mark the body bogus.
- `msgHeader` normalizes headers to CRLF, appends final blank line, parses MIME headers and envelope addresses, and synthesizes `From`/`Date` when needed.
- MIME parsers populate `Header` fields: `mimeType`, `mimeParams`, `mimeEncoding`, `mimeId`, `mimeDescription`, `mimeDisposition`, `mimeMd5`, `mimeLanguage`.
- Address parser handles atoms, quoted strings, comments, groups/routes partly, local names, and bang paths via `headAddress`, `headAddrSpec`, `domBang`, `headDomain`.
- `selectFields` copies matching or non-matching header fields for IMAP `BODY.PEEK[HEADER.FIELDS...]` style responses.
- `freeMsg`, `cleanupHeader`, `freeMAddr`, `freeMimeHdr` own recursive cleanup.

Integration points:
- Used by mailbox open, fetch, search, and store paths through `Msg`, `Header`, `MAddr`, and helper functions such as `msgSize`, `msgStruct`, `msgFile`.
- Depends on Plan 9 `upas/fs` message directory conventions: `info`, `raw`, `rawbody`, `rawheader`, `mimeheader`, `unixheader`.
- Uses global `username`, `site`, and temporary file helper `imapTmp`.

Risks and notes:
- Header parsing is permissive and hand-written; malformed input can trigger fallback/bogus paths rather than strict rejection.
- Bogus-message handling synthesizes multipart content with stripped and base64 alternatives, preserving access to corrupted original data.
- `mimeLanguage` loops while `headChar(0) != ','` and consumes with `headChar(1)`; malformed endings rely on `headChar`/NUL behavior.
