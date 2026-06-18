# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/a.h

Declares the shared interface and constants for `htmlroff`, a troff-to-HTML converter.

Key points:
- Defines private Unicode/rune sentinels for HTML-sensitive/raw characters, nonbreaking space, empty output, formatted diversion markers, and symbol variants.
- Defines units (`UPI`, `UPX`) and input mode bits (`CopyMode`, `ExpandMode`, `ArgMode`, `HtmlMode`).
- Declares request/escape registration, macro/string/register operations, input stack operations, HTML output/tag functions, roff evaluation, output functions, warning/allocation helpers, and section initializers `t1init` through `t20init`.
- Declares global state such as control characters, output buffer, input mode, request state, verbosity, and line position.
- Defines rune allocation convenience macros and installs `%L` format checking.

Dependencies and interactions:
- Included by all `htmlroff` source files.
- Coordinates the central dispatcher in `roff.c` with section-specific modules.

Research relevance:
- This header is the primary internal contract for the `htmlroff` interpreter/converter.
