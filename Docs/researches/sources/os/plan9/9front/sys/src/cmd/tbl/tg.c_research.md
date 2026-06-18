# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tg.c

Processes `T{ ... T}` multiline text blocks inside table cells.

Key points:
- `gettext` starts a diversion for the current text block, appends it to the right-column register macro, and emits setup for fill mode, fonts, point size, vertical spacing, line length, and indentation.
- Reads lines until `T}` or `T}<tab>`; missing terminator resets `iline` to the starting line before reporting an error.
- Stores diversion height and width in registers named from `texname`.
- Copies any text after `T}<tab>` back into the caller buffer as remaining cell content.
- Advances `texname` through `texstr` and returns the diversion character used for the text block.
- `untext` restores no-fill table mode and line length after text-block processing.

Dependencies and interactions:
- Calls `gets1`, `match`, `tcopy`, `reg`, `ctspan`, `ctype`, and `rstofill`.
- Uses globals `textflg`, `texname`, `texstr`, `texct`, `vsize`, `cll`, `tab`, and line/column style arrays.

Research relevance:
- This is the bridge between `tbl` cells and troff diversions for multiline formatted text.
