# File Research: sources/os/plan9/9front/sys/src/cmd/rc/trap.c

Trap dispatcher for `rc`. Maintains global pending trap counts by signal and total `ntrap`.

`dotrap()` runs pending signal handlers by looking up variables such as `sigint`; if a handler function exists it starts it with a copy of `$*`. In child processes it exits. For unhandled interactive interrupt/quit, it unwinds to the command-reading loop; other unhandled traps exit except ignored `sigwinch`.
