# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/mail

## Purpose
Plan 9 `rc` wrapper for the `mail` command.

## Behavior
With no arguments it execs `upas/nedmail`. For flags matching reader-style options (`-f*`, `-r*`, `-c*`, `-m*`) it also execs `upas/nedmail`; otherwise it execs `upas/marshal` to compose/send mail.

## Dependencies
Plan 9 `rc`, `upas/nedmail`, `upas/marshal`.

## Risks / Notes
This is dispatch glue; behavior is entirely determined by first argument shape.
