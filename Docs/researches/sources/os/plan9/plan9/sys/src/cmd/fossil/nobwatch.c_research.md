# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/nobwatch.c

No-op replacement for `bwatch.c`.

It defines the same block-watch functions but each either does nothing or marks its argument used. This lets builds disable the slow debug lock-order checker without changing callers.
