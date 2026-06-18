<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/options.py -->
# sources/sync-backup/bup/lib/bup/options.py

## Purpose
This standalone-style module parses bup option specification strings into command usage text, getopt option sets, defaults, aliases, negated options, and an attribute-accessible option dictionary.

## Important APIs, Types, And Functions
Important pieces are `OptDict`, `Options`, `_intify()`, `_tty_width()`, `Options.parse()`, and `Options.parse_bytes()`.

## Control Flow
`Options.__init__()` stores the optspec and calls `_gen_usage()`, which parses synopsis lines until `--`, builds short/long getopt declarations, records defaults from bracket suffixes, creates aliases including `no-` forms, and formats usage. `parse()` runs the configured getopt function, loads defaults into `OptDict`, handles help/usage, converts digit aliases and integer-looking parameters, increments flag counts for repeated booleans, and returns `(opt, flags, extra)`.

## State And Persistence Behavior
Option state is per `Options`/`OptDict` instance. There is no file persistence. `OptDict` caches alias lookups and invalidates the cache on writes.

## Dependencies And Integration Points
It depends only on standard `getopt`, `textwrap`, terminal sizing, and regex. It is used by command modules such as `ls.py` and many bup commands, while `helpers.py` imports `_tty_width` for column formatting.

## Risks And Edge Cases
Specs are parsed with simple string/regex rules, so malformed specs may produce odd aliases instead of explicit failures. `--no-*` aliases are generated for all long options, including options with parameters, which command code must interpret carefully. `_intify()` converts only exact decimal strings, leaving other numeric-looking values as strings. `parse_bytes()` decodes with surrogateescape to preserve arbitrary argv bytes.

## Test Signals
`test/int/test_options.py`, command usage tests, and command-specific CLI tests validate defaults, aliasing, negation, digit options, byte argv decoding, help output, and fatal error behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/options.py -->
