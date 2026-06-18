# File Research: sources/os/plan9/9front/sys/src/cmd/acme/edit.h

This header defines Acme edit-command parser data structures and prototypes.

Key contents:
- `String`: mutable rune string with length and allocation size.
- `Addr`: parsed address node for character/line/regex/current/end/range forms.
- `Address`: evaluated `Range` plus owning `File`.
- `Cmd`: parsed command node with optional address, regex, nested command, text, move/copy target address, count, flags, command character, and next command.
- `cmdtab` declaration describes command parsing and dispatch metadata.
- `List`: generic growable pointer list used to track parser allocations.
- Default address enum: `aNo`, `aDot`, `aAll`.
- Prototypes for command functions, string allocation, parser helpers, address evaluation, execution, and error reporting.

Filesystem/storage relevance:
- Indirect: edit commands operate on `File` and `Text`, and this header defines the parse tree passed to file-changing logic.

Notes:
- Uses Plan 9 vararg checking for `editerror`.
- `INCR` controls parser allocation-list growth.
