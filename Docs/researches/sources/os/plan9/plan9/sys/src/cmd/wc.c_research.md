# File Research: sources/os/plan9/plan9/sys/src/cmd/wc.c

This is a Plan 9 `wc` implementation with rune awareness.

Options:
- `-l` lines.
- `-w` words.
- `-r` runes.
- `-b` bad runes.
- `-c` bytes/chars by file offset.
- Defaults to line, word, and byte counts when no flags are given.

Counting behavior:
- Uses `Bgetrune`, so UTF text is counted as runes.
- `Runeerror` increments bad-rune count and is excluded from line/word classification.
- Word state toggles between `Space` and `Word` using `isspacerune`.
- Byte count is taken from `Boffset`.

Output:
- `report` builds a single aligned line containing requested counts and optional filename.
- Totals are accumulated and printed when multiple files are processed.

Error handling:
- Failed file opens call `perror`, set final status to `"can't open"`, and continue.
