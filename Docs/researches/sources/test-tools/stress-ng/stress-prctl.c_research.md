# sources/test-tools/stress-ng/stress-prctl.c

Purpose: `stress-prctl.c` implements the `prctl` stressor, forking short-lived children that exercise a broad cross-section of Linux `prctl()` and x86 `arch_prctl()` operations, including valid get/set round trips and deliberately invalid argument paths.

Important APIs/types/functions: `stress_arch_prctl()` covers x86-64 CPUID, FS/GS, and XCOMP permission queries/requests. `stress_prctl_syscall_user_dispatch()` optionally installs SIGSYS handling and validates `PR_SET_SYSCALL_USER_DISPATCH` by trapping `kill()`. `stress_prctl_child()` contains the main catalogue: capabilities, child subreaper, dumpability, endian/fp/SVE/SME modes, tagged addresses, MCE kill, `PR_SET_MM`, names, no-new-privs, pdeathsig, ptracer, seccomp query, securebits, THP, perf events, timerslack, speculation control, IO flusher, sched core, memory merge, PAC, VMA naming, auxv, RISC-V/PPC/shadow-stack/timer/futex/indirect-branch/rseq controls, and invalid command checks.

Control flow: the top-level function mmaps one anonymous page for VMA naming, synchronizes, and loops. Each iteration forks a child; the child applies scheduler settings and runs `stress_prctl_child()`, returning failure only for unexpected successes/failures on checked invalid paths. The parent waits and aborts the stressor on nonzero child exit, otherwise increments bogo ops.

State and persistence behavior: state is mostly process attributes inside forked children, so mutations such as no-new-privs, names, timerslack, seccomp queries, speculation settings, and VMA names do not escape the child except where prctl semantics are system/global. The parent owns the anonymous page and unmaps it at deinit.

Dependencies and integration points: Linux `sys/prctl.h`, many UAPI option macros, optional `asm/prctl.h`, optional seccomp headers, signal handlers, environment/auxv discovery, mmap helpers, fork retry, and `CLASS_OS` registration with `VERIFY_ALWAYS`.

Risks: this file is highly kernel-version and architecture dependent; most blocks are compile-time guarded but runtime `EINVAL`/`ENOSYS` is expected for newer or unsupported controls. Some `PR_SET_MM` and capability operations require privileges and are intentionally ignored. Syscall user dispatch temporarily changes signal handling and must disable dispatch before returning from SIGSYS.

Test signals: direct `--prctl` should fork repeatedly without child failure. Useful validation includes kernels with new prctl constants, x86 syscall user dispatch, unprivileged runs where privileged calls fail harmlessly, and unexpected success checks for invalid commands.
