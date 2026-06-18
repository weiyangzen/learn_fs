# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/a.h

Central header for `htmlroff`, a troff/ms-to-HTML converter.

- Defines private Unicode/rune sentinels for raw HTML characters, symbols, formatted/unformatted markers, nonbreaking space, and output-control markers.
- Defines unit constants and input mode flags: copy, expand, argument, and HTML modes.
- Declares nearly all parser, request, macro, input, output, register, string, HTML, font, and utility functions.
- Declares global parser/output state such as `backslash`, `bol`, `bout`, `dot`, `inputmode`, `inrequest`, `utf8`, `verbose`, and `linepos`.
- Provides rune allocation/reallocation/move macros and `Fmt` pragma for `%L`.

This header binds together the larger `htmlroff` implementation beyond the files in this group.
