# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/edit.h

This header defines the parse-tree structures and public parser/executor interfaces for Acme `Edit`.

Key contents:
- `String`: mutable rune string with allocation size.
- `Addr`: address AST node supporting numeric, regexp, dot/dollar, relative, comma, semicolon, and file-match forms.
- `Address`: evaluated range plus target `File`.
- `Cmd`: command AST node with optional address, regexp, text, move/copy target address, nested command, next command, count, flags, and command char.
- `cmdtab` declaration describing command syntax and executor callback.
- `List`: growable typed pointer list used for parse allocation tracking.
- Default address enum: `aNo`, `aDot`, `aAll`.
- Function prototypes for command handlers, parser helpers, and edit execution.

Filesystem relevance:
- Defines the command structures used for file/range edits and file selection in Acme.
