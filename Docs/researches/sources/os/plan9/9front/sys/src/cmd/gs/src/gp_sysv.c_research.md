# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_sysv.c

Compatibility implementations for older System V Unix platforms.

Key behavior:
- Provides `rename` using `access`, `unlink`, `link`, and final `unlink` of the source.
- Provides `gettimeofday` using `times`, `time`, and a cached offset from process ticks to wall-clock seconds.
- Uses `HZ` from system headers or defaults to 100.

Research notes:
- Comments state this file is not used for SVR4 platforms.
- The fallback `rename` is not equivalent to modern atomic `rename`.
