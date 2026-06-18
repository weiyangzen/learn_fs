# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/syscallargs.awk

This AWK script generates assembly constants for or1k syscall argument counts. It reads syscall number definitions and `check_syscall_args...` records from syscall headers, maps each syscall name to either zero or `sizeof(struct sys_*_args) / sizeof(register_t)`, and emits `define NSYSARGS_<name> <count>` lines.

The output also includes required headers for `genassym`. `SYS.h` uses these generated `NSYSARGS_*` constants to decide whether to load seventh and eighth syscall arguments from the user stack.
