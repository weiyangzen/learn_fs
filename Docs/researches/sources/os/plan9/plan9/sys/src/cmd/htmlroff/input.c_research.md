# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/input.c

Input stack implementation for `htmlroff`.

- Defines `Istack` entries for file-backed input, string-backed input, unget runes, line number, logical name, completion callback, and next pointer.
- Supports pushing or queueing input files, stdin, and strings.
- Maintains current top `istack` and bottom `ibottom`.
- Updates `.F` and `.B` registers/strings with current file name and basename-like value.
- `getrune()` reads from unget buffer, string buffer, or `Biobuf`, popping exhausted sources automatically.
- `ungetrune()` pushes back up to three runes, creating an empty input frame if necessary.
- Provides line formatting and line-number/name update helpers.

Dependencies are Plan 9 `bio`, rune helpers, and register/string helpers declared in `a.h`.

Notable concerns: unget storage is small, and input-source ownership is manual. `dup(0, b->fid)` is used to make a Bio wrapper around stdin via an initially opened `/dev/null`.
