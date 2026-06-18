# File Research: sources/os/plan9/9front/sys/src/cmd/sam/cmd.c

`cmd.c` is sam's command reader and parser. `cmdtab` defines the command language: command character, whether it accepts text/regex/address/count/token arguments, default command/address, and execution function.

Input comes from command-buffer replay, the downloaded terminal protocol, or stdin. `inputc`, `inputline`, `getch`, `nextc`, and `ungetch` provide rune-level parsing, while `cmdloop` repeatedly parses, executes, updates files, and synchronizes the terminal.

The parser builds `Cmd`, `Addr`, and `String` objects into temporary lists so `freecmd` can release all parse artifacts after each command.

`parsecmd` handles addresses, command lookup, two-character `cd`, regex arguments, substitution right-hand sides, destination addresses for move/copy, default nested commands, text collection, token collection, braced command groups, and newline validation.

`getregexp` preserves the last non-empty regex as sam's implicit pattern. `simpleaddr` and `compoundaddr` parse address syntax and insert implicit `+` where sam grammar requires it between adjacent address terms.

The command input path also integrates with downloaded `samterm`: `termcommand` copies new command-file text into `termline`, and `cmdloop` unlocks terminal UI state and emits pattern/current-file updates.
