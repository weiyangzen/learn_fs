# File Research: sources/os/plan9/9front/sys/src/cmd/init.c

Implements Plan 9 user-space `init`.

Key points:
- Closes inherited boot fds, parses service mode (`-c` cpu, `-t` terminal) and manual mode (`-m`), and optional rc command.
- Sets process priority through `#p/<pid>/ctl`.
- Reads CPU type, user, and system name from kernel devices/environment and sets `objtype`, `service`, and timezone environment files.
- Calls `newns` to build the namespace for the current user.
- On CPU service and non-manual startup, runs `/rc/bin/cpurc` first.
- Main loop repeatedly starts `/bin/rc`, then falls into manual mode after rc exits.
- `fexec` forks a child exec function, forwards interrupts to the child process group via `notepg`, handles wait races/notes, and sleeps forever if exec failed.
- `rcexec` chooses rc command according to command/manual/cpu/terminal mode.
- `readfile`, `readenv`, `setenv`, and `cpenv` support environment setup.
- `procopen` opens process control files and logs warnings.

Dependencies and interactions:
- Uses Plan 9 auth namespace setup, process note handling, `/env`, `#c`, `#e`, and `#p` devices.

Research relevance:
- Central boot/userland process supervisor for Plan 9/9front sessions.
