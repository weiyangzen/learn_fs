# File Research: sources/os/plan9/9front/sys/src/cmd/db/format.c

Purpose: Format-string execution for `db` memory, symbol, and literal printing.

Key behavior:
- `scanform()` repeats an entire format over a count, updating `dotinc`.
- `exform()` executes individual format modifiers, reads from a `Map` unless in literal mode, prints values, and updates `dot`.
- Supports address/symbol formats, signed/unsigned/octal/hex 16-bit and 32-bit formats, 64-bit formats, bytes/chars/runes/strings, instructions, hex instructions, floats/doubles, newlines, quoted text, cursor movement, and source-line format `z`.
- Instruction formats call `machdata->das()` and `machdata->hexinst()`.
- Float formats call machine-specific float conversion helpers.
- `printesc()` prints non-printable bytes as `\xNN`.
- `inkdot()` advances `dot` with wraparound detection.

Notable details:
- First-pass logic prints a symbol/address prefix and warns on unaligned instruction addresses.
- Literal mode treats `dot` itself as the value rather than reading memory.
