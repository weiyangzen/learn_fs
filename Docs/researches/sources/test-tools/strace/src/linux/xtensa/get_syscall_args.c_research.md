<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/xtensa/get_syscall_args.c

Purpose: extracts Xtensa syscall arguments from windowed registers.
Important APIs/types/functions: `arch_get_syscall_args`, `xtensa_probe_naregs`, `set_regs`, `n_args`, and register order `{6,3,4,5,8,9}`.
Control flow: probes the number of address registers once by temporarily moving `windowbase`, restores registers, then masks window-relative register indexes while filling `tcp->u_arg`.
State and persistence behavior: caches `naregs_mask` statically and writes per-syscall arguments. Dependencies and integration points: all Xtensa syscall decoders.
Risks: the probe mutates registers temporarily; failed restore would be severe. Test signals: Xtensa argument-order tests and builds with different register-window sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_syscall_args.c -->
