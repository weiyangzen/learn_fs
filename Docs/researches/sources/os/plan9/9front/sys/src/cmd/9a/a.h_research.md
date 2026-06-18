# File Research: sources/os/plan9/9front/sys/src/cmd/9a/a.h

Shared header for the PowerPC64 assembler `9a`.

Key contents:
- Includes Plan 9 libc/bio headers, PowerPC64 object interface `../9c/9.out.h`, and common compiler compatibility support.
- Defines assembler limits for symbols, buffers, include stack, history, macro count, and allocation hunks.
- Defines `Sym`, `Io`, `Gen`, and `Hist` used for symbols/macros, input stack, assembled operands, and file history records.
- Declares global lexer/parser/assembler state including include paths, input buffers, symbol table, current line, pass number, output file, pc, debug flags, and `Biobuf` output.
- Declares parser, lexer, macro preprocessor, object emission, history emission, error, include, and portability wrapper functions.
- `Gen` supports symbol, offset, type, register, index register, name class, mask, float value, and 8-byte string literal operands.

Filesystem relevance: indirect. It is assembler infrastructure for building PowerPC64 Plan 9 code.
