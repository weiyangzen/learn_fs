# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_xxx.c

Read completely: 181 lines.

Contains miscellaneous kernel entry points: reboot/powerdown helpers, stack-smash panic support when propolice/ret-protector are not used, and optional syscall debugging traces.

Reboot and power handling:
- `sys_reboot()` requires superuser privileges, stops secondary CPUs on multiprocessor kernels, and calls `reboot()` with the requested flags.
- `reboot()` stops periodic RTC syncing, sets the global `rebooting` flag, and calls machine-dependent `boot()`.
- `do_powerdown()` sends `SIGUSR2` to init once when `allowpowerdown` is enabled, then disables further automatic powerdown requests.
- `powerbutton_event()` ignores events during resume when suspend support says the system is resuming, otherwise queues `powerdown_task` on `systq`.

Safety/debug support:
- `__stack_smash_handler()` panics with the damaged function name for builds without propolice and return protector support.
- Under `SYSCALL_DEBUG`, `scdebug_call()` and `scdebug_ret()` print syscall entry/return diagnostics for unimplemented/out-of-range calls by default, or all calls when configured. Argument display is controlled by `SCDEBUG_SHOWARGS`; `lseek` return formatting handles `off_t`.

Global state:
- `rebooting` indicates reboot is in progress.
- `powerdown_task` is a taskqueue item wrapping `do_powerdown()`.
- Optional `scdebug` bit flags control syscall debug verbosity.
