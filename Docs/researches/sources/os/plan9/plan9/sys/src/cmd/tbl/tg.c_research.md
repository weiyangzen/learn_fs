# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tg.c

Processes multiline `T{ ... T}` text blocks inside table cells.

Key functions:
- `gettext` creates a troff diversion for the text block, applies font/size/vertical spacing and line length, reads until `T}`, records diversion height/width registers, and returns a small identifier stored as a pointer-like value.
- `untext` restores fill mode and line length after text diversions.

Notable behavior:
- Uses `texstr` characters as diversion names and errors when exhausted.
- Handles `T}` followed by the table delimiter by copying remainder back into the current cell buffer.
- Text block line length depends on explicit `w(...)`, column span, and current right register.
