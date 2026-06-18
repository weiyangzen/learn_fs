# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/word.c

Manages `Word` linked lists and parses strings into words.

Key functions:
- `newword()`, `wdup()`, `delword()` allocate/copy/free words.
- `stow()` splits a string into a word list.
- `wtos()` joins a word list with a separator.
- `nextword()` parses one word, handling whitespace, quotes, escapes, and `$` variable expansion.
- `dumpw()` prints word lists for debugging.

Behavior notes:
- Variable expansion can splice multiple words into the output list.
- If a variable expansion is empty at the start of a word, parsing restarts.
- Uses `Bufblock` for incremental UTF-aware construction.
