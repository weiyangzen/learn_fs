# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccons.c

Interactive fossil console implementation.

It maintains shared input/output ring queues, supports multiple console opens, and starts reader/writer threads per attached console. `consProc` assembles command lines, echoes input, handles control editing (`^D`, backspace, newline, `^U`, `^W`, delete), runs completed lines through `cliExec`, and redraws the prompt.

`consTTY` attaches the process to `/dev/cons` or `#c/cons` in raw mode. `consWrite` writes to the console queue when open and falls back to fd 2 when no console is attached.
