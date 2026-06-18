# File Research: sources/os/plan9/9front/sys/src/cmd/va/a.h

`a.h` is the shared header for the MIPS assembler variant `va`. It defines symbol, operand (`Gen`), input stack, and history structures; assembler constants; global parser/lexer state; symbol tables; include/macro state; and prototypes for lexing, preprocessing, assembly passes, object emission, and diagnostics.

It includes MIPS object definitions from `../vc/v.out.h` and compiler compatibility helpers. The header binds the yacc grammar and lexer/body include files into one old-style Plan 9 assembler architecture.
