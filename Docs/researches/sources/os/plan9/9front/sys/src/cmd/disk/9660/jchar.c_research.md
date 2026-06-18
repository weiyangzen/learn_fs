# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/jchar.c

Joliet string conversion, validation, sorting, and secondary volume descriptor writing.

Key behavior:
- `jolietstring` converts big-endian two-byte UCS-style names into UTF strings and interns them.
- `isbadjoliet` rejects names longer than 64 runes and characters forbidden by Joliet.
- `jolietcmp` compares basename and extension as rune sequences.
- `Cputjolietsvd` writes the Joliet secondary descriptor, including UCS-2 Level 2 escape sequence `%/C`, metadata strings, root placeholder, and dates.

Notable dependencies:
- Rune helpers from `rune.c`.
- Directory entry writer `Cputjolietdir`.

Research notes:
- The comparison mirrors ISO sorting but on encoded runes.
- Fixed-size local rune arrays are marked with a `/*BUG*/` comment for long names.
