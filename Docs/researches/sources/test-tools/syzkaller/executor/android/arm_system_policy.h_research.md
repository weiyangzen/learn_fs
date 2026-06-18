# sources/test-tools/syzkaller/executor/android/arm_system_policy.h

Purpose: This generated Android BPF policy defines the system-account syscall allowlist for 32-bit ARM. It is selected for `GOARCH_arm` when the Android seccomp account is system.

Important APIs and types: It exports `const struct sock_filter arm_system_filter[]` and `arm_system_filter_size`. The policy is a classic BPF decision tree over syscall numbers.

Control flow and state: The generated code permits broader privileged ranges than app policy, including mount/chroot/accounting/reboot/module/time/setuid/setgid-related calls while preserving the generated trap fallback through the wrapper. It performs no architecture validation itself and stores no runtime state.

Dependencies and integration points: `android_seccomp.h` includes this file, chooses it for `SCFS_SystemAccount`, adds architecture checks for `AUDIT_ARCH_ARM`, and installs the combined filter with `prctl`.

Risks and test signals: Risks include stale Android policy generation, jump offset corruption, and divergence from arm app policy where system-only allowances are expected. Tests should include BPF load/install on ARM, comparison with current `genseccomp.py` output, and probes for both system-allowed and denied syscalls.
