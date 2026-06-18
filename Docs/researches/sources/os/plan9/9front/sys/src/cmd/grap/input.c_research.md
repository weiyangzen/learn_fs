# File Research: sources/os/plan9/9front/sys/src/cmd/grap/input.c

Input, macro, copy, and error subsystem for `grap`. It maintains nested source stacks for files, strings, macros, pushed chars, `thru` expansions, and free-on-pop strings. It supports `define`, argument substitution `$n`, delimited body capture, file inclusion, `copy thru` line-to-macro expansion, `until` termination, pushback, and contextual error reporting.

It also provides math error checking and shell command assembly/execution. EOF handling restores previous files and emits `.lf` line directives for downstream troff/pic diagnostics.
