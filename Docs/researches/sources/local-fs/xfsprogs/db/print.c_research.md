# File Research: sources/local-fs/xfsprogs/db/print.c

## Purpose
Implements structure and string printing for the current xfs_db typed cursor.

## Main Interfaces
- Registers `print` / `p` through `print_init()`.
- Exports `print_flist()`, `print_sarray()`, `print_struct()`, and `print_string()`.

## Control Flow
`print_f()` requires a current type with a pfunc and invokes it in `DB_READ` mode. `print_struct()` prints all fields when no field names are supplied or parses requested field expressions. `print_flist_1()` recursively walks parsed field lists, builds dotted/indexed names, bounds array printing to the current buffer length, and calls field-type print functions. `print_sarray()` prints arrays of substructures in compact bracketed form.

## Dependencies
Uses the field/flist/field-attribute systems, type descriptors, string-vector helpers, output helpers, signal interrupt checks, and IO cursor state.

## Risks And Invariants
- Field parsing and printing are tied to `iocur_top->data` and current type metadata.
- Array printing guards against reading past the current buffer when possible.
- Field types without print functions must be explicitly marked empty-capable or they print an unrecognized/type-mismatch diagnostic.
