# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/fns.h

This header declares dtracy’s internal functions across parser, lexer, type checker, code generator, action builder, runtime parser, and aggregation modules.

Important exported groups:
- Parser/lexer: `yyparse`, `yylex`, `yyerror`, `lexinit`, `lexstring`, `node`, `getsym`.
- Type and formatting: `exprcheck`, `type`, `addtype`, `evalop`, `nodetfmt`, `typetfmt`, `typefmt`, `nodefmt`.
- Clause/action generation: `clausebegin`, `addstat`, `addarg`, `addprobe`, `addpred`, `clauseend`, `packclauses`, `actgradd`, `tracegen`, `codegen`.
- Runtime parsing: `addepid`, `parsebuf`.
- Aggregation: `aggparsebuf`, `aggnote`, `aggdump`, `agginit`.

Important implementation notes:
- It aliases no implementations; it is purely a shared declaration surface.
- `#pragma varargck argpos error 1` is declared in `dat.h`, while `fns.h` exposes the variadic `error`.
