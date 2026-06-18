# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/input.c

This file implements `grap` input management: nested files, strings, macros, one-character pushback, `copy thru`, macro arguments, and error-context reporting.

`pushsrc`/`popsrc` maintain a source stack. `definition`, `delimstr`, `dodef`, and `getarg` collect macro bodies and arguments. `input` and `nextchar` multiplex source types and support `$N` macro argument expansion.

`do_thru` reads data lines, splits fields into macro arguments, stops on `.G2` or an `until` string, and pushes the thru macro for each data row.

The file also implements `copyfile`, `copydef`, `copythru`, `copyuntil`, `copy`, shell-command collection/execution helpers, math `errcheck`, and `yyerror` context printing.
