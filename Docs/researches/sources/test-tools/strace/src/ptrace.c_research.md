# sources/test-tools/strace/src/ptrace.c

Purpose: Main decoder for the `ptrace` syscall, including request-specific formatting and register/regset helpers.

Important APIs/types/functions: `SYS_FUNC(ptrace)`, `decode_ptrace_entering`, `decode_ptrace_exiting`, `decode_peeksiginfo_args`, `decode_seccomp_metadata`, `decode_getregset`, `decode_setregset`, and `print_user_offset_addr`.

Control flow: entry decoding prints request, pid, address, and data according to request semantics. Some requests complete on entry, while output-producing requests defer data printing to exit. Regset requests preserve original `iov_len` in `tcb` private storage and compare it with exit length. Exit decoding prints peek results, event messages, siginfo, sigmasks, seccomp filters/metadata, syscall info, and register blocks.

State and persistence: uses `set_tcb_priv_ulong`/`get_tcb_priv_ulong` to persist regset lengths across syscall entry/exit. Otherwise stateless.

Dependencies/integration: includes ptrace command xlat tables, compat ptrace tables, `printsiginfo`, `ptrace_syscall_info`, `regs.h`, iovec helpers, seccomp filter printers, and architecture register decoders.

Risks: ptrace has architecture-specific argument reversals (SPARC), compat request namespaces, and conditional request availability. Incorrect phase handling can print output before kernel writes it. Regset length mutation must be shown accurately.

Test signals: ptrace peek/poke, get/set siginfo, get/set sigmask, get/set regset, seccomp metadata/filter, syscall info, compat personality, SPARC/IA64 conditional builds, and xlat verbosity modes.
