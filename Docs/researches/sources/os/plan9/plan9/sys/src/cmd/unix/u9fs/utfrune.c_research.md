# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/utfrune.c

- Role: UTF-aware equivalent of `strchr` for searching a rune in a UTF string.
- Key function: `utfrune(s, c)` uses `strchr` for ASCII-compatible runes and `chartorune` for multibyte runes.
- Integration: Used by `getfields` delimiter matching.
- Risks/notes: Invalid UTF advances by `chartorune`’s error length of 1.
