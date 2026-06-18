# File Research: sources/os/bsd/netbsd-src/lib/libedit/parse.c

## Purpose
Parses libedit configuration commands and key-binding escape strings.

## Main Interfaces
- `parse_line`: tokenizes a wide command line and dispatches it.
- `el_wparse`: command dispatcher used by configuration loading and public parse APIs.
- `parse__escape`: decodes `^X`, backslash escapes, octal escapes, and `\U+xxxx` Unicode escapes.
- `parse__string`: converts an escaped binding string to raw wide characters.
- `parse_cmd`: resolves a command name to a numeric editor action.

## Command Dispatch
`el_wparse` supports optional `prog:command` prefixes. When present, it matches the prefix against `el->el_prog` using `el_match`; non-matching prefixed commands are ignored. Matching commands are dispatched through a static table that routes names such as binding, terminal, editor, and tty configuration commands to their subsystem handlers.

## Dependencies
Uses the wide tokenizer API (`tok_winit`, `tok_wstr`, `tok_wend`), `el_match` from search utilities, map help tables, and libedit allocation helpers.

## Risks And Notes
Escape parsing is deliberately permissive for common readline/editrc forms but returns `NULL` or `-1` on malformed control/Unicode sequences. Binding code must check those failures before mutating maps.
