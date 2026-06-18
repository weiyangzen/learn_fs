# sources/security-integrity/libcap/psx/psx_syscall.h

Purpose: public C header for libpsx syscall synchronization.

Important APIs/types: defines `LIBPSX_MAJOR`, `LIBPSX_MINOR`, variadic macro `psx_syscall()`, functions `__psx_syscall()`, `psx_syscall3()`, `psx_syscall6()`, `psx_load_syscalls()`, enum `psx_sensitivity_t`, and `psx_set_sensitivity()`.

Control flow/integration: macro appends sentinel argument counts so `__psx_syscall()` can infer 0-6 supplied arguments. Function-pointer consumers can use fixed 3- and 6-argument wrappers. `psx_load_syscalls()` supports weak-symbol override in libraries such as libcap.

State and dependencies: no state in the header; declares process-wide behavior implemented by `psx.c`.

Risks and test signals: variadic macro cannot be used as a function pointer, and callers should avoid using PSX for read-only syscalls. Version and sensitivity contracts are checked indirectly by C and Go tests.
