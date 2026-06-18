# File Research: sources/os/plan9/plan9/sys/src/cmd/fmt.c

Paragraph formatting utility.

Key behavior:
- Reads stdin or listed files, parses words with indentation, and emits wrapped lines.
- Supports `-i indent`, `-j` to disable joining original lines, and `-l`/`-w` for line width.
- Respects `$tabstop` for indentation width.
- Maintains paragraph breaks via blank-line sentinel words.
- Adds two spaces after sentence-ending punctuation except short uppercase abbreviations.

Important implementation details:
- `indentof()` computes leading spaces/tabs and preserves current indent on whitespace-only lines.
- `parseline()` builds a dynamic `Word**` list for the whole input.
- `printwords()` wraps by UTF rune length, indent changes, width, and `join` policy.

Risks and invariants:
- The entire input's word list is accumulated before printing.
- Allocation failures are not checked in `addword()`.
