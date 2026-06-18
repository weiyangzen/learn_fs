# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/ts.c

Contains small string and numeric helper routines for `tbl`.

Key points:
- `match` checks full string equality.
- `prefix` checks whether one string is a prefix of another.
- `letter`, `digit`, `numb`, and `max` provide simple character/integer utilities.
- `tcopy` copies a NUL-terminated string.

Dependencies and interactions:
- Used by parser, text-block handling, numeric splitting, and option logic.

Research relevance:
- Utility file with no table-specific state, but used broadly by the command.
