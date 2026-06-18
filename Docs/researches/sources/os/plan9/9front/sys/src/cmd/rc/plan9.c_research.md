# File Research: sources/os/plan9/9front/sys/src/cmd/rc/plan9.c

Plan 9-specific runtime backend for `rc`. Defines builtins, default `Rcmain`, fd path prefix, signal names, environment import/export, process creation, wait handling, directory iteration, file operations, and prompts.

Environment variables and functions are synchronized through `/env` and `/env/fn#*`. `Vinit()` imports `/env`; `Updenv()` writes changed variables/functions back.

`Fork()` uses `rfork(RFPROC|RFFDG|RFREND)`. `Waitfor()` handles Plan 9 `Waitmsg` status strings and routes unrelated child statuses to waiting pipeline frames.
