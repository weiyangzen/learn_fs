# File Research: sources/os/plan9/plan9/sys/src/cmd/dc.c

This file is a complete implementation of Plan 9 `dc`, the arbitrary-precision reverse-Polish calculator.

Key behaviors:
- Represents numbers and strings as `Blk` buffers with read/write cursors.
- Uses base-100 internal numeric digits plus a trailing scale byte for decimal scale.
- `main()` initializes buffered I/O, calculator state, then enters `commnds()`.
- `commnds()` is the command interpreter for arithmetic, stack operations, registers, arrays, macros, conditionals, shell escapes, input execution, scale/input-base/output-base changes, and printing.
- Arithmetic core includes `add()`, `subt()`, `mult()`, `div()`, `dcexp()`, `dcsqrt()`, `scale()`, `removc()`, `removr()`, and `dscale()`.
- Input/output conversion includes `readin()`, `dcprint()`, `tenot()`, `oneot()`, `hexot()`, and `bigot()`.
- Register and array support uses a fixed 256-slot symbol table, with stackable symbols and array registers starting at `ARRAYST`.
- Macro execution uses `readstk` and block-backed strings.
- Memory management uses `salloc()`, `copy()`, `more()`, `release()`, `morehd()`, and a simple free list of `Blk` headers.

Notable command coverage:
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `^`, `v`.
- Stack: `p`, `P`, `f`, `d`, `c`, `z`, `Z`.
- Scale/base: `k`, `K`, `i`, `I`, `o`, `O`, `X`.
- Registers: `s`, `S`, `l`, `L`.
- Arrays: `:`, `;`.
- Macros/control: `[ ... ]`, `x`, `?`, `!`, `<`, `>`, `=`, `q`, `Q`.

Notable implementation details:
- Division keeps quotient in the return value and remainder in global `rem`; fractional remainder support also uses `irem`.
- Negative numbers are represented by complement-like digit handling via `chsign()`.
- Output base selection switches between decimal, unary-like, hex fast path, and general-base rendering.
- `command()` executes shell commands through `/bin/rc -c`.
- `Y` is a debug command that dumps allocator and stack statistics.
- The garbage collector hook exists but is empty; allocation failures abort through `ospace()`.
