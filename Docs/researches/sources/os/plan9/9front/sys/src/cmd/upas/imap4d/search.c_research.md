# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/search.c

Evaluates parsed IMAP search trees against `Msg` objects.

Key responsibilities:
- Performs case-insensitive substring searches over files, headers, addresses, and metadata.
- Determines whether a search requires only flags, `info`, or full message body/header structure.
- Evaluates flag, size, address, subject, date, UID/sequence set, header, body, text, `NOT`, and `OR` criteria.

Important functions:
- `filesearch()` scans a message file in overlapping buffers.
- `headersearch()` selects matching header fields and searches the value.
- `addrsearch()` formats parsed addresses and searches them.
- `datecmp()` compares parsed message dates against search dates.
- `searchld()` is intended to compute load depth, but currently always returns `0` at the end despite setting `r`.
- `msgidsearch()` optimizes `Message-ID` matching.
- `searchmsg()` evaluates all search keys.

Filesystem relevance:
- Opens message files such as `body` through `msgfile()`.
- Triggers `msginfo()` or `msgstruct()` depending on needed data.

Notable risks:
- `searchld()` appears buggy: it accumulates `r` but returns `0`, preventing intended lazy loading hints.
- Date searches assume relevant `info` date fields are present and parseable.
- Header/text search does not decode MIME encoded words, as noted by comment.
