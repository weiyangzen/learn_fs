# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_scdebug.c

## Purpose

`kern_scdebug.c` provides syscall debugging support when `SYSCALL_DEBUG` is enabled, plus indirect syscall implementations included from generated `sys_syscall.c`.

## Main Responsibilities

- Includes generated indirect syscall handlers twice:
  - once as `sys_syscall`;
  - once as `sys___syscall`.
- Under `SYSCALL_DEBUG`, defines runtime flags:
  - `SCDEBUG_CALLS`
  - `SCDEBUG_RETURNS`
  - `SCDEBUG_ALL`
  - `SCDEBUG_SHOWARGS`
  - `SCDEBUG_KERNHIST`
- Exposes global `scdebug`, defaulting to calls, returns, and arguments.
- Supports optional KERNHIST logging.
- Initializes the kernel history buffer in `scdebug_init()` when both syscall debug and kernhist are enabled.

## Call Logging

- `scdebug_call(code, args)`:
  - checks `SCDEBUG_CALLS`;
  - locates current process, emulation, and sysent entry;
  - skips invalid/unimplemented syscalls unless `SCDEBUG_ALL` is set;
  - logs to kernhist if requested, using literal-only format strings and avoiding `%s`;
  - otherwise prints process ID, command, emulation name, syscall number/name, and argument values.

## Return Logging

- `scdebug_ret(code, error, retval)`:
  - checks `SCDEBUG_RETURNS`;
  - applies the same invalid/unimplemented filtering;
  - logs or prints syscall return error and two return values.

## Compat/Emulation Notes

- `CODE_NOT_OK` accounts for `__HAVE_MINIMAL_EMUL`.
- The code avoids assuming every emulation has the same syscall table size or names.
