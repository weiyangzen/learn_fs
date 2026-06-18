# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/system.c

Implements `system(const char *command)` using `posix_spawn()` of `_PATH_BSHELL` with arguments `sh -c -- command`. For `command == NULL`, it checks executable shell availability with `access()`.

For actual commands, it ignores `SIGINT`/`SIGQUIT` in the parent, blocks `SIGCHLD`, arranges child signal defaults/mask through spawn attributes, locks `environ` while spawning, waits for the child with `waitpid()`, and restores signal state before returning the wait status or `-1`.
