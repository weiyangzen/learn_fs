# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/io.c

Purpose: Interactive input parsing helpers for `pdisk`.

Input buffering:
- Maintains a small custom unget buffer with `my_getch()` and `my_ungetch()`.
- `flush_to_newline()` consumes pending input, optionally preserving newline.

Command parsing:
- `get_command()` prompts and returns the next nonblank command character.
- `get_okay()` prompts for yes/no confirmation with a default on newline.
- `bad_input()` prints an error and flushes the rest of the input line.

Argument parsing:
- `get_number_argument()` parses an optional decimal number from input.
- Internal `get_number()` accepts only decimal digits followed by whitespace/newline.
- `get_dpistr_argument()` parses Apple partition strings, accepting quoted strings or unquoted names containing letters and selected punctuation.
- Internal `get_string()` reads up to `DPISTRLEN` bytes and returns a newly allocated copy.

Units/modifiers:
- `get_multiplier()` parses `k`, `m`, `g`, or `t` suffixes relative to a divisor, with overflow protection for terabyte scaling.
- `get_partition_modifier()` recognizes a trailing `p`/`P`.
- `number_of_digits()` supports table formatting.

Integration:
- Used by interactive `pdisk.c` operations for command, base, size, type, name, and confirmation prompts.
