# File Research: sources/os/plan9/plan9/sys/src/9/boot/sac.c

Special SAC boot method that bypasses normal root-server connection.

Key behavior:
- `configsac()` rebuilds namespace, binds `#C`, sets sysname and hostowner to `brick`, and execs `/<cputype>/init -c`.
- `connectsac()` is unreachable and returns `-1`.

This is a hardwired boot path for a specific standalone/control environment.
