# File Research: sources/os/plan9/9front/sys/src/cmd/rc/getflags.h

Header for the flag parser. Defines `NFLAG` as 128 and exposes `flag`, `cmdname`, `flagset`, and `getflags()`.

Used by `exec.c`, `lex.c`, platform files, and other `rc` modules to test shell options.
