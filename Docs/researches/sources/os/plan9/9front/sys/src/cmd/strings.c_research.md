# File Research: sources/os/plan9/9front/sys/src/cmd/strings.c

`strings.c` implements a Unicode-aware `strings` utility.

Behavior:
- Usage: `strings [-m min] [file...]`.
- Default minimum span is 6 printable runes.
- Reads from stdin when no files are supplied.
- For multiple files, prints a `filename:` header before each file’s strings.
- Uses `Bgetrune` to scan runes rather than raw bytes.
- Once a printable run reaches `minspan`, prints the byte-ish `Boffset(&fin)-minspan` offset followed by the accumulated string, then streams further printable runes until a non-printable rune terminates the string.

Printability:
- `isprint` rejects `Runeerror`.
- Accepts ASCII space through `~` and runes above `0xA0`.

Risks:
- Offset calculation subtracts rune count, not encoded byte length, so offsets for non-ASCII UTF input may be approximate relative to bytes.
- Function name `isprint` shadows the libc/ctype concept, but signature uses `Rune`.
