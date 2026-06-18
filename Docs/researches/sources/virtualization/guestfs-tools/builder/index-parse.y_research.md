# File Research: sources/virtualization/guestfs-tools/builder/index-parse.y

## Scope

Bison grammar for virt-builder index files, including optional clear-signed PGP wrappers.

## Grammar And Behavior

- Parses an empty index, plain section list, or PGP prologue + section list + epilogue.
- A section is `[name]` followed by zero or more fields.
- Fields may have continuation lines; continuations are concatenated with newline separators.
- Builds linked `struct section` and `struct field` lists from scanner tokens.
- Uses destructors to free partially parsed sections/fields on parse errors.

## Interfaces

- Exposes `do_parse(struct parse_context *, FILE *)`.
- Uses `scanner_init`, `scanner_destroy`, and reentrant `yylex`.
- Reports syntax errors with optional program name, input file, line number, and configured suffix.

## Risks And Invariants

- Memory ownership transfers from scanner token values into linked parser structures.
- `concat_newline` allocates merged strings and must be paired with freeing old values.
- Parser is pure/reentrant and depends on `YY_EXTRA_TYPE` carrying parse context through the scanner.
