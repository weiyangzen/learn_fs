# File Research: sources/os/plan9/9front/sys/src/cmd/aux/na/na.y

`na.y` is a yacc grammar and implementation for an NCR53c8xx SCRIPTS assembler. It preprocesses an input file through `cpp`, parses labels, constants, externs, expressions, SCSI phases, register names, move/select/reselect/jump/call/int/set/clear/nop/return/de fw instructions, and emits a C initializer `unsigned long na_script[]`.

The assembler performs two passes. Pass 1 builds symbols and computes `dot`; pass 2 prints instruction longwords with source-line comments, records patch entries, emits `NA_SCRIPT_SIZE`, `na_patches[]`, external enum values, label enums, and constant defines.

It has a typed expression system: constants, addresses, table addresses, externs, registers, unknowns, and errors. Type tables determine legal arithmetic; patch types are generated for address, register, extern, and certain immediate/register move cases.

The lexer supports decimal, octal, hex, and binary integers; symbols; comments beginning with `;`; and `#line` directives from cpp. It recognizes a large token table for NCR/SCSI register names and instructions.

Risk points: fixed limits for cpp options, patches, external symbols, source line length, and filename length; some range checks only warn under `wflag`; relative address encoding is 24-bit signed and may zero bad values.
