# File Research: sources/os/plan9/plan9/sys/src/9/boot/testboot.c

Small test harness for boot-style filesystem servers.

Key behavior:
- Usage: `testboot cmd args...`.
- Creates a pipe, forks, execs the requested command with pipe as stdin/stdout, then mounts/amounts the pipe endpoint at `/n/kremvax`.

Useful for testing a boot server command outside the full boot sequence.
