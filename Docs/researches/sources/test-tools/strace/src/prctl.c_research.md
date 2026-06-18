<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/prctl.c -->
# sources/test-tools/strace/src/prctl.c

Purpose: comprehensive decoder for `prctl` and x86 `arch_prctl`.

Important APIs/types/functions: `SYS_FUNC(prctl)`, `SYS_FUNC(arch_prctl)`, `print_prctl_args`, `print_get_uint_arg`, `print_set_kulong_arg`, SVE/SME/tagged-address/RISC-V value formatters, seccomp filter decoding, capability and architecture xlat tables.

Control flow: `prctl` prints the option then dispatches through a large option switch grouped by common decoding style. It handles no-arg getters, pointer-output getters on exit, setters with symbolic flags, seccomp filters, capabilities, securebits, timerslack, MCE, `PR_SET_MM`, vector length controls, speculation controls, PAC, tagged address, syscall user dispatch, sched core cookies, MDWE, RISC-V/PPC controls, VMA names, and ptracer ids. Getter results often return aux strings on exit. `arch_prctl` has x86-specific pointer-output and xfeature cases.

State and persistence behavior: no persistent global state; uses syscall enter/exit phase and `tcp->auxstr` for decoded return values.

Dependencies and integration points: integrates with syscall tables, seccomp BPF decoder, pid/signal/capability printers, architecture conditionals, and many generated prctl xlat tables.

Risks: prctl grows frequently and option-specific unused-argument rules differ. Some symbolic values are architecture-specific or not public UAPI. Return decoding must happen only on successful exits.

Test signals: representative option from each switch group, seccomp strict/filter, get/set aux-string options, SVE/SME/tagged/RISC-V formatting, sched core get cookie, VMA name, ptracer any, unknown option fallback, and x86 arch_prctl cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/prctl.c -->
