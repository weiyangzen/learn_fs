# File Research: sources/os/plan9/9front/sys/src/cmd/pic/input.c

## Role

Implements `pic` input source stacking, macro definitions/expansion, argument parsing, pushback, file inclusion, `copy thru`, shell escapes, and syntax-error context reporting.

## Source Stack

`pushsrc` and `popsrc` manage a stack of input sources: files, macros, single pushed-back chars, thru markers, literal strings, and strings to free. `input` reads through `nextchar`, records context for errors, and triggers `do_thru` when a `copy thru` line expansion is pending.

`unput` pushes a character back through both the pushback buffer and source stack.

## Macros

`definition` reads a delimited macro body and installs it as a `DEFNAME`. `dodef` parses macro arguments in parentheses, stores them in an argument frame, and pushes the macro body. Macro expansion substitutes `$N` arguments.

`delimstr` reads balanced delimited bodies, supporting paired delimiters such as `{}`.

## Copy/Thru

`copyfile`, `copydef`, `copythru`, `copyuntil`, and `copy` coordinate copying from files and applying a macro to each input line. `do_thru` tokenizes each line into macro arguments, terminates on `.PE` or an optional until string, and pushes the thru macro.

## Errors And Shell

`yyerror` reports file/line and calls `eprint`, which prints nearby input and pushback context, then pushes `.PE` as a recovery guard.

`shell_init`, `shell_text`, and `shell_exec` collect and run `rc -c` commands.
