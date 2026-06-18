# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/summary.c

Extracts document summary metadata and language information.

Key responsibilities:
- Stores title, subject, author, app name, manager, company, creation date, last-save date, and language ID.
- Converts DOS date strings, Word DTTM values via helpers, and OLE FILETIME values.
- Parses OLE SummaryInformation and DocumentSummaryInformation property sets.
- Reads legacy Word for DOS and WinWord 1/2 summary/associated-string fields.
- Maps Word language IDs to locale-like strings.

Important behavior:
- String properties are trimmed at both ends and ignored if empty.
- OLE property streams may live in small or big block depots depending on stream size.
- Word 8 Far East documents may use an alternate language ID header field.
- Getter functions return static formatted date buffers for PDF/XML metadata.

Dependencies:
- OLE PPS stream info, block readers, time conversion helpers, allocation wrappers.

Notable risks:
- OLE property parsing assumes validated offsets after header checks.
- The language mapping is partial and returns `NULL` for unknown IDs.
