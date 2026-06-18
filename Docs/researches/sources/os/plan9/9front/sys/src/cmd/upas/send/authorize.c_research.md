# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/authorize.c

`authorize()` runs a rewrite-rule authorization command stored in `dest.repl1`. A zero exit status authorizes forwarding; a nonzero status records stderr in `dest.repl2` and changes status to `d_noforward`.

The function marks `dp->authorized` before starting the command to avoid repeated authorization loops. It uses the shared process API, reads stderr to completion, waits, and frees process state. Failure to start the process is treated as forwarding disallowed.
