# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.y

Yacc grammar and support code for `na`, an NCR53c8xx SCRIPTS assembler. It preprocesses one input file through `/bin/cpp`, performs a first parse to resolve labels/symbols, then a second parse to emit C initializers for `na_script[]`, relocation/patch metadata, external symbol enums, label enums, and constant defines.

Core behavior:
- Defines NCR53c8xx instruction grammar for `MOVE`, `SELECT`, `RESELECT`, `WAIT`, `JUMP`, `CALL`, `RETURN`, `INT`, `INTFLY`, `SET`, `CLEAR`, `NOP`, and `DEFW`.
- Tracks assembler location counter `dot` in bytes while emitting 32-bit script words.
- Implements symbol typing with `Const`, `Addr`, `Table`, `Extern`, `Reg`, `Unknown`, and `Error`.
- Uses expression type tables to reject invalid arithmetic such as multiplying addresses or mixing incompatible symbolic types.
- Computes relative branch addresses with signed 24-bit range checking.
- Emits patch entries for address/register/external operands through `patchtype()` and `fixup()`.

Important functions:
- `main()` parses `-D` cpp options, preprocesses input, runs pass 1/pass 2, and emits output C.
- `yylex()`, `yygetc()`, `yyrewind()` implement the lexer, including `#line` handling from cpp.
- `setsym()`, `findsym()`, `eval()` manage symbol table and typed expressions.
- `regmove()` encodes register/SFBR move and ALU forms.
- `chkreladdr()` decides whether an operand can be compiled as relative now or needs patching.
- `fixup()` emits `struct na_patch na_patches[]`, `NA_PATCHES`, external enums, label enums, and constants.

Dependencies and integration:
- Includes Plan 9 libc plus local `na.h`.
- Calls `/bin/cpp` with `-+ -N` and user `-D` options.
- Output is generated C data intended to be compiled into a NCR SCSI driver or related firmware/script consumer.

Notable risks:
- Fixed-size arrays: `MAX_PATCHES` is 1000 and `externp` has 100 slots without robust overflow checks in all paths.
- Lexer line buffer is fixed at 500 bytes.
- `eval()` divides without checking zero divisor.
- `preprocess()` does not inspect child exit status beyond `wait()`.
