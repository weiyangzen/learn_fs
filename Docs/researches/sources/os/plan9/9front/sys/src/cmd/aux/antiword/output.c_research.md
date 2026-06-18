# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/output.c

Generic output dispatcher that routes document events to text, formatted text, PostScript, XML, or PDF backends.

Key responsibilities:
- Creates and destroys `diagram_type` output contexts.
- Reads current options, records active conversion type and encoding, and calls backend prologue/epilogue functions.
- Dispatches image prologue/epilogue and dummy-image insertion.
- Dispatches second-stage document setup: PS fonts, XML book intro, PDF info dictionary and fonts.
- Routes line movement, substrings, paragraph boundaries, page boundaries, headers, lists, list items, table ends, and table rows to supported backends.
- Maintains common behavior such as advancing `pDiag->lXleft` after substring output.

Dependencies:
- Depends on backend modules for TXT/FMT/PS/XML/PDF functions and on global options from `options.c`.

Notable risks:
- Backend selection is global after prologue, so mixed simultaneous output contexts are not supported.
- Unsupported conversion/event combinations usually no-op rather than report errors.
