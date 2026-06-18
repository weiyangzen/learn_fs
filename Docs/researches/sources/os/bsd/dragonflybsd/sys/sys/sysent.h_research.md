# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysent.h

Kernel syscall dispatch table and executable ABI vector definitions.

Key contents:
- Defines `sy_call_t`, the syscall handler signature:
  - `int (*)(struct sysmsg *, const void *)`
- Defines `struct sysent`:
  - argument count
  - result size
  - start handler
  - optional abort handler for async calls
- Defines `struct sysentvec`, describing an executable ABI’s syscall table, signal mappings, stack fixup, signal delivery, sigcode, coredump hook, image activation hook, and minimum signal-stack size.
- Kernel-only dynamic syscall module support:
  - `struct syscall_module_data`
  - `SYSCALL_MODULE`
  - `SYSCALL_MODULE_HELPER`
  - `syscall_register`
  - `syscall_deregister`
  - `syscall_module_handler`

Important behavior:
- `NO_SYSCALL` is `-1`.
- `SYSCALL_MODULE_HELPER` calculates argument count from the generated args struct minus `struct sysmsg`.
- `struct sysentvec` is the bridge between syscall dispatch and binary compatibility/personality handling.

Research notes:
- This is central to kernel syscall dispatch and loadable syscall modules.
- The ABI vector is broader than syscall dispatch: it also owns signal and core-dump behavior.
