# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exec.h

## Role

`exec.h` defines kernel exec subsystem interfaces and shared exec data structures. It covers executable magic probing, exec argument state, interpreter recursion, aux-vector construction, exec module registration, ELF/brand helpers, and core dump helper prototypes.

## Public And Kernel Structures

- Defines `MAGIC_BYTES` and `getexmag()` for executable magic inspection.
- Defines `execa_t` for filename/argv/envp syscall arguments.
- Defines `execenv_t` for bss/brk bases, brk size, executable vnode, and magic.
- Kernel-only `uarg_t` carries exec argument counts/sizes, pathnames, aux vector size, stack layout/alignment/protection, model conversion info, pointer sizes, `execsw` entry, entry point, thread pointer, executable vnode, emulator/brand data, auxv stack addresses, credential state, environment scrubbing flag, and commpage address.
- Defines brand actions `EBA_NONE`, `EBA_NATIVE`, and `EBA_BRAND`.
- Defines stack helper macros `execpoststack()` and `stackaddress()`.
- `ADDAUX()` writes aux vector entries and clears padding where ABI alignment creates possible padding.
- Defines interpreter path size and recursion depth with `INTPSZ` and `INTP_MAXDEPTH`, and `intpdata_t` for nested interpreter names/args.
- Defines set-id classification bits `EXECSETID_SETID`, `EXECSETID_UGIDS`, and `EXECSETID_PRIVS`.

## Exec Switch

`struct execsw` stores magic string, magic offset/length, exec callback, core callback, and module lock pointer. The header declares `nexectype`, `execsw[]`, `execsw_lock`, standard magic values/strings, exec argument parsing, common exec entry points, exec switch allocation/lookup, permission checks, segment mapping, exec environment setup, executable open/close, register setup, and stack pointer sizing.

## ELF, Brands, And Core Dumps

Declares ELF exec and map/read helpers for native and LP64/ELF32 cases, including brand-aware `mapexec_brand()` and `mapexec32_brand()`. Also declares `core_seg()` and `core_write()` for exec module core dump routines.
