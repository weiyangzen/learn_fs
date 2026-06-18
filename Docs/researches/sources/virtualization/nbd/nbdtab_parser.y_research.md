# File Research: sources/virtualization/nbd/nbdtab_parser.y

## Purpose
Defines the bison grammar for parsing `nbdtab` entries into client configuration callbacks.

## Main Grammar
- `nbdtab` accepts empty input, blank lines, or repeated mount definitions.
- `mountdef` parses `device host exportname` followed by an optional option list, then calls `nbdtab_commit_line()`.
- `option` supports bare flags via `nbdtab_set_flag()` and key/value properties via `nbdtab_set_property()`.

## Dependencies
Includes `nbdclt.h` for callback declarations and client-related types. Uses `char *` semantic values provided by the lexer.

## Risks and Notes
The grammar assumes a compact whitespace-sensitive format with exactly one `SPACE` token between required fields. It delegates all semantic validation to callback implementations.
