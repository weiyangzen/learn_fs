# File Research: sources/os/plan9/9front/sys/src/cmd/read.c

Implementation of the Plan 9 `read` command. Copies requested input from files or stdin to stdout by lines, bytes, or runes.

Options: `-m` reads multiple lines indefinitely, `-n nlines`, `-c nbytes`, and `-r nrunes`. Rune mode preserves whole UTF sequences and warns on partial trailing runes.

Exit status is `eof` only when no data is read before EOF.
