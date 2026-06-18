# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/addr.c

This file parses and evaluates Acme address expressions over text buffers.

Key behavior:
- `isaddrc()` and `isregexc()` define conservative address/regexp character classes for expansion.
- `number()` converts line or character numeric addresses into `Range`s, handling forward/backward relative movement.
- `regexp()` compiles and searches regex addresses forward or backward.
- `address()` evaluates address syntax including `.`, `$`, `#n`, line numbers, `+`, `-`, `/re/`, `?re?`, `,`, and `;`.

Important details:
- `;` updates the base address for the right side; `,` does not.
- Character addresses use `#`; line addresses are default.
- Missing left side of `,` defaults to start, and missing right side defaults to end.
- Invalid addresses can warn and set `evalp = FALSE` rather than aborting, depending on caller context.

Filesystem relevance:
- Indirect but important for Acme’s file-opening syntax like `file:addr`, and for `addr` pseudo-file behavior.
