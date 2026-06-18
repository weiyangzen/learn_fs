# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_syscalls.c

## Purpose

`kern_syscalls.c` provides dynamic syscall slot registration for loadable modules. It lets modules claim `sys_lkmnosys` placeholder entries in `sysent`, restore prior entries on unload, and chain module event handlers.

## Main Contents

- `sys_lkmnosys()` behaves like `sys_nosys()` but is identifiable as a reserved dynamic syscall placeholder.
- `syscall_register()`:
  - If `*offset == NO_SYSCALL`, scans `sysent[1..SYS_MAXSYSCALL)` for the first `sys_lkmnosys` slot.
  - Validates explicit offsets.
  - Rejects slots already occupied by non-placeholder handlers.
  - Saves the old `sysent` and installs the new one.
- `syscall_deregister()` restores the old `sysent` for a nonzero offset.
- `syscall_module_handler()`:
  - On `MOD_LOAD`, registers the syscall, stores the assigned offset in module-specific data, then invokes an optional chained event handler.
  - On `MOD_UNLOAD`, invokes the chain first and restores the syscall slot only if the chain succeeds.
  - For other module events, delegates to the chained handler or returns success.

## State And Dependencies

The file mutates the global `sysent` table and depends on syscall numbers, `struct syscall_module_data`, module-specific storage, and the normal `sys_nosys()` signal behavior from `kern_sig.c`.

## Risks And Invariants

Registration assumes placeholder slots are preinstalled as `sys_lkmnosys`. There is no visible locking in this file, so callers/module loading must provide sufficient serialization. The unload order intentionally lets chained handlers veto before the syscall entry is restored.
