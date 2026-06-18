# File Research: sources/os/plan9/9front/sys/src/cmd/aux/tablet.c

`tablet` bridges `/dev/tablet` motion lines into `/dev/mousein`. It reads lines beginning with `m x y b ...`, parses x/y/buttons, and writes `A x y b` events to mouse input.

It exits fatally on open or read failure and ignores non-motion or malformed lines. The local file has 31 lines, while the work item metadata listed 32.
