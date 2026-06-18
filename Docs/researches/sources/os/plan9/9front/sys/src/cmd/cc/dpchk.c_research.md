# File Research: sources/os/plan9/9front/sys/src/cmd/cc/dpchk.c

Purpose: Implements compiler pragma handling for vararg format checking, packing, floating-point rounding, profiling, and incomplete struct/union declarations.

Key points:
- Maintains format flag classification in `flagbits` and format/type prototype lists `Tprot` and `Tname`.
- `arginit` initializes default printf-style flag parsing and builtin integer format aliases.
- `pragvararg` parses `#pragma varargck` forms for argument position, format type, and ignored flags.
- `getflag` parses a format sequence, tracking ignored flags, width `*` arguments, length modifiers, and verb bits.
- `newprot` records accepted type/format flag combinations.
- `newname` records functions whose format argument should be checked.
- `dpcheck` detects registered vararg calls, finds the format argument, verifies it is a constant char string, and checks remaining arguments.
- `checkargs` compares parsed format directives against actual argument types and warns on mismatch, missing arguments, extra arguments, and invalid `*` width types.
- `pragpack`, `pragfpround`, and `pragprofile` parse on/off or numeric pragma state.
- `pragincomplete` marks struct/union types or tags as intentionally incomplete and supports `_on_`/`_off_` debug toggles.

Dependencies and interactions:
- Includes `cc.h` and generated `y.tab.h`.
- Uses parser/lexer helpers such as `getsym`, `getnsn`, `getnsc`, `getr`, `getc`, and `unget`.
- Uses type comparison helpers `sametype`, `beq`, `bor`, `blsh`, and `bset`.
- Called from semantic function-call checking in `com.c`.

Research notes:
- Format checking is driven by pragmas rather than hardcoded knowledge of every function.
- The format parser supports UTF/rune decoding via `chartorune` and `runetochar`.
