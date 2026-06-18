# File Research: sources/os/plan9/plan9/sys/src/9/teg2/lproc.s

Small process-transition assembly support.

Key behavior:
- `touser(SP)`: performs the first jump from kernel to user mode by installing user SP, setting user-mode SPSR, pushing PC `UTZERO+0x20`, and using `RFEV7W`.
- `forkret`: returns a newly forked process through the same saved-`Ureg` return path as traps.

Notes:
- This file is the bridge between scheduler-created kernel frames and first user-mode execution.
