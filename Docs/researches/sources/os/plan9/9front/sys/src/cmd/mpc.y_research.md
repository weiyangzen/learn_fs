# File Research: sources/os/plan9/9front/sys/src/cmd/mpc.y

Yacc grammar and code generator for a small multiprecision arithmetic language. It parses functions and emits C functions using Plan 9’s `mp` library.

Language features:
- Function definitions with argument lists and statements.
- Expressions over names, numeric constants, calls, comma lists, unary minus, arithmetic, shifts, exponentiation, assignments, ternary expressions, and boolean comparisons.
- Statements for assignment, expression/call, `mod` scoped modular arithmetic, `if`/`else if`/`else`, `while`, `break`, and blocks.
- Lexer supports comments beginning with `#`, identifiers, numbers, keywords, operators, and shifts/equality tokens.

Code generation:
- Builds `Node` ASTs and interned `Sym` records with flags for set/use/argument/local status.
- Performs constant folding with multiprecision arithmetic where safe, including modular folding when the active modulus is constant.
- Emits `mpint *` temporaries with reuse/free tracking.
- Emits optimized cases for constants `mpzero`, `mpone`, `mptwo`, shifts, doubling, modular add/sub/mul, modular inverse/division, exponentiation, and branchless conditional selection with `mpsel` for expression conditionals.
- Tracks assigned locals, initializes them with `mpnew(0)`, and frees locals/temporaries on exit or break.
- Reports diagnostics with source filename and AST context using custom `%N` and `%B` formatters.

Important interactions:
- Uses Plan 9 `libmp` primitives such as `mpadd`, `mpsub`, `mpmul`, `mpdiv`, `mpmod`, `mpexp`, `mpinvert`, `mpmodadd`, `mpmodsub`, and `mpmodmul`.
- Reads stdin or files with `Biobuf`, repeatedly invoking `yyparse` until EOF.

Notable quirks:
- The compiler enforces “name used but not set.”
- Some operations fall through intentionally for folding/generation paths.
- Modular division is implemented by modular inverse followed by multiply.
