# sources/test-tools/syzkaller/executor/android/arm64_system_policy.h

Purpose: This generated Android BPF policy defines the allowed syscall set for system-account execution on AArch64. It is smaller than the app policy source file but includes privileged/system ranges needed by Android system processes.

Important APIs and types: It exports `const struct sock_filter arm64_system_filter[]` and `arm64_system_filter_size`. The filter is a BPF syscall-number decision tree ending in allow for matched ranges.

Control flow and state: The wrapper loads the syscall number first; this policy then branches through generated `BPF_JGE` and `BPF_JEQ` checks. Its comments show allowed ranges including mount/chroot/accounting/module/syslog/reboot/set*id and clock/time operations that differ from restricted app policy. No local state is modified.

Dependencies and integration points: It integrates only through `android_seccomp.h`, which chooses it when `set_app_seccomp_filter(SCFS_SystemAccount)` is called on arm64 and adds arch validation/trap behavior.

Risks and test signals: The security boundary is entirely encoded in generated jump offsets; manual edits are high risk. Test signals include BPF verifier acceptance, parity with Android bionic generation, exercising representative system-only syscalls, and ensuring app-vs-system selection does not swap filters.
