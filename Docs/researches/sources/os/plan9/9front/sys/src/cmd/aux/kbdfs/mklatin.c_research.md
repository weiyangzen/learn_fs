# File Research: sources/os/plan9/9front/sys/src/cmd/aux/kbdfs/mklatin.c

Role: Generator for `latin1.h` compose table used by `kbdfs`.

Input:
- Parses `/lib/keyboard` style lines where the leading hex rune is followed by one or more compose sequences.
- Ignores blank and comment lines.

Data structure:
- Builds a trie keyed by compose-sequence prefixes, with each trie node holding possible final bytes and corresponding output runes.
- Ensures prefix entries are emitted before longer entries, matching assumptions in `kbdfs`.

Output:
- Prints table rows of leading sequence string, possible final-character string, and either a wide string literal of output runes or an integer array when `-r` is used.
- Escapes C string characters safely.

Constraints:
- `MAXLD` is 2 because `kbdfs` assumes compose lead strings are at most two bytes.
