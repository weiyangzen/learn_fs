# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/nlist.c

Setup and name-table implementation for `cpp`.

`setup` installs preprocessor keywords and built-ins, configures Plan 9 include search paths from `$objtype`, `/sys/include`, `$include`, and `-I`, handles options such as `-N`, `-D`, `-U`, `-M`, `-V`, `+`, `-i`, `-P`, and `-.`, opens input/output files, and pushes the initial source.

`lookup` is a 128-bucket hash table keyed by token text. Installing a name also sets the quick lookup bit used by the lexer/macro expander.
