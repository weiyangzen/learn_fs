# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/deadlock

Plan 9 rc helper for running an acid deadlock inspection against fossil processes.

It locates `8.fossil` or `fossil` pids when none are supplied, prints matching process lines, generates an acid script that includes `fossil-acid`, runs `deadlocklist`, and filters the marked output range.

This is a debugging script outside the compiled fossil server.
