# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diffio.c

Input, verification, and output formatting support for the local `diff` implementation.

Key behavior:
- `readline` reads one bounded logical line from a `Biobuf`, truncating overly long physical lines after `MAXLINELEN-1` bytes and discarding the remainder.
- `readhash` hashes lines for the LCS engine, with `bflag` modes for exact text, coalesced whitespace, or all-whitespace stripping.
- `prepare` opens a file, detects likely binary input by scanning up to 1024 bytes as UTF, then builds the per-line hash array for text files.
- `check` rereads both files to build byte-offset arrays and validates hash-derived matches against actual text, clearing false matches.
- `fetch` prints ranges with prefixes and emits the standard “No newline at end of file” diagnostic when needed.
- `change` emits normal, ed, reverse-ed, and `-n` style hunks immediately, while context/unified/all-context modes accumulate `Change` records.
- `flushchanges` groups nearby accumulated changes and prints context, all-context, or unified diff hunks.

Notable dependencies:
- Plan 9 `Biobuf` I/O.
- Shared `Diff`, `Change`, and global mode flags from `diff.h`.

Research notes:
- The binary heuristic rejects NUL and C1/control-like Unicode range `0x80..0xa0`, then lets `diffreg.c` perform byte comparison.
- `ixold`/`ixnew` offsets are central to both hunk printing and `merge3`.
- The whitespace handling in hashing is intentionally rechecked with squished full lines to avoid hash-only matches.
