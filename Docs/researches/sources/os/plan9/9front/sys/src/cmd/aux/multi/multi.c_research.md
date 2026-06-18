# File Research: sources/os/plan9/9front/sys/src/cmd/aux/multi/multi.c

`multi.c` is the runtime dispatcher for binaries produced by `mkmulti`. It includes generated `multiproto.h` and `multi.h`, maps command names to renamed `main` functions, and invokes the matching function with `argv` shifted so the selected command sees itself as `argv[0]`.

It strips any path prefix from the requested command name. If called without a command, or if no command matches, it prints an error and exits.
