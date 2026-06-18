# File Research: sources/os/plan9/plan9/sys/src/cmd/look.c

Read fully: 347 lines, 6034 bytes. SHA-256 prefix: `5d1941acf5ef799d`.

This is a Plan 9 implementation of `look`, performing binary search over a sorted dictionary and printing matching entries. It supports directory-order filtering, case folding, interactive stdin keys, numeric comparison, custom field terminator, exact matching, and an alternate dictionary file.

Important routines:
- `locate()` binary searches to the first possible matching line.
- `acomp()` compares runes with prefix-aware return codes.
- `torune()` converts UTF strings.
- `rcanon()` canonicalizes through terminator, directory filtering, case folding, and Latin-1 fold table.
- `ncomp()` compares numeric fields including sign, integer and fractional parts.
- `getword()` reads newline-delimited rune records.

Integration: uses `Biobuf` rune I/O and defaults to `/lib/words`.

Risk notes: reverse numeric order is declared but not implemented beyond `rev=1`. Word buffers are fixed at `WORDSIZ`.
