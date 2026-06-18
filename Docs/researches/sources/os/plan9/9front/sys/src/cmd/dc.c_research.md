# File Research: sources/os/plan9/9front/sys/src/cmd/dc.c

Purpose: Arbitrary-precision reverse-polish desk calculator.

Core representation:
- `Blk` is a growable byte buffer with read/write/begin/end pointers.
- Numbers are stored in base-100 digits, with the last byte used as scale in stack values.
- Negative values use a sign/complement convention manipulated by `chsign()`.
- Stack is `Blk *stack[STKSZ]`; registers/symbols use `Sym` lists and `stable[TBLSZ]`.
- Arrays are stored as pointer blocks through `Wblk` overlay operations.

Important behavior:
- `main()` initializes bio and calls `init()` then `commnds()`.
- `commnds()` is the command interpreter. It handles numeric input, arithmetic, scale/base changes, stack ops, register save/load, arrays, macro strings, macro execution, conditional execution, shell escapes, and printing.
- Arithmetic includes `add()`, `subt()`, `mult()`, `div()`, `dcsqrt()`, and `dcexp()`.
- Scale handling uses `eqk()`, `dscale()`, `add0()`, `removc()`, `removr()`, `scale()`, and `scalint()`.
- Output supports decimal, arbitrary output base, base 1/0 special cases, and character/string printing through `dcprint()`, `tenot()`, `oneot()`, `hexot()`, and `bigot()`.
- Input/macro execution uses `readc()`, `unreadc()`, `readstk`, strings `[ ... ]`, and command `x`.
- Shell escape `!` runs `/bin/rc -c`.
- Memory management uses `salloc()`, `copy()`, `more()`, `seekc()`, `release()`, and a free-list of `Blk` headers.

Notable details:
- Debug command `Y` prints allocator and stack statistics.
- `init()` can read commands from a file argument after checking it is not a directory.
- `garbage()` is a stub; allocation failures retry once and then call `ospace()`.
