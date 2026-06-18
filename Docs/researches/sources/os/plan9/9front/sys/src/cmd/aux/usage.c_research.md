# File Research: sources/os/plan9/9front/sys/src/cmd/aux/usage.c

`usage` prints a generated usage line using environment variables. It reads `$0`, `$flagfmt`, and `$args`, derives the command basename, and writes `usage: <cmd> ...` to stderr.

`flagfmt` syntax is parsed as comma/space separated flag descriptors. Single-letter flags without arguments are grouped into one `[-abc]`; flags with argument names print as `[-x arg]`. It handles UTF-8 flag runes.

It exits with status `usage` and reports an error if `$0` is missing.
