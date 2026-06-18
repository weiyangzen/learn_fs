# File Research: sources/os/plan9/9front/sys/src/cmd/rc/subr.c

Small utility module for `rc`: checked allocation, strdup, source-location printing, integer-to-ASCII conversion, and panic handling.

`panic()` prints through the shell’s `err` stream and calls the platform `Abort()`.
