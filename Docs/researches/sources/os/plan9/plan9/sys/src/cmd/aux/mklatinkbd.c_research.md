# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mklatinkbd.c

This file converts keyboard composition data into a Latin keyboard table.

Key behavior:
- Parses `/lib/keyboard`-style lines containing Unicode code points and composition sequences.
- Builds a trie of byte sequences up to length two.
- Emits table rows sorted so longer prefix-dependent sequences appear before shorter ones.
- Can emit rune integer arrays with `-r` instead of wide string literals.

Important details:
- Warns on duplicate sequence definitions.
- Escapes generated C string bytes safely.
- Input defaults to stdin unless a file is provided.

Filesystem relevance:
- Indirect build utility for keyboard input tables.
