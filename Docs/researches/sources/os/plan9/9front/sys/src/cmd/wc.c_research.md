# File Research: sources/os/plan9/9front/sys/src/cmd/wc.c

Plan 9 `wc` implementation for UTF-encoded text. It counts lines, words, runes, bad runes, and bytes using a table-driven byte-state machine.

Key behavior:
- Default output is line, word, and byte counts; flags add/select line, word, rune, bad-rune, and byte columns.
- `count()` reads in `IOUNIT` chunks, increments byte/rune counters optimistically, and adjusts rune/bad-rune counts based on UTF continuation-state transitions.
- Four 256-entry state tables distinguish whitespace, word body, and pending 2/3/4-byte UTF sequences.
- A final non-ground UTF state increments the bad-rune count for trailing partial runes.
- Multiple input files accumulate totals and print a `total` row.

Notable dependencies:
- Plan 9 UTF conventions and libc I/O.

Research notes:
- The header documents known limitations: whitespace is only space/tab/newline, impossible-rune bytes are not separately counted, and non-canonical UTF encodings are not specially counted.
