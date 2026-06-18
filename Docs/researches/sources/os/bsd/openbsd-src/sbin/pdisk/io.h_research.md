# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/io.h

Purpose: Public prototypes for `pdisk` interactive input helpers.

Declared API:
- Numeric/unit helpers: `get_multiplier()`, `get_number_argument()`, `number_of_digits()`.
- Input/error helpers: `bad_input()`, `flush_to_newline()`, `my_ungetch()`.
- Prompt helpers: `get_command()`, `get_okay()`, `get_partition_modifier()`, `get_dpistr_argument()`.

Integration:
- Included by `pdisk` command and dump code.
- Depends on `DPISTRLEN` from partition map definitions for string semantics in the implementation.
