# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.y

Yacc grammar for the Lucent awk parser.

Defines awk program structure, patterns, actions, expressions, statements, function definitions, regex literals, array references, redirections, `getline`, loops, `BEGIN`/`END`, `pat,pat` ranges, and built-in function syntax. Semantic actions build `Node` trees using helpers from `parse.c` such as `stat*`, `op*`, `linkum`, `makearr`, and `pa2stat`.

Important parser-side state:

- `beginloc`, `endloc`: accumulated `BEGIN` and `END` statement lists.
- `infunc`: tracks function definition context for `return`, `next`, and argument handling.
- `inloop`: validates `break` and `continue`.
- `curfname`, `arglist`: current function metadata.

The grammar performs compile-time validation for unsafe redirections/pipes in safe mode, duplicate function definitions, array/function name conflicts, illegal `index()` regex use, duplicate arguments, and null-pattern truth coercion through `notnull()`.
