# sources/test-tools/syzkaller/executor/android/x86_system_policy.h

Purpose: This generated Android BPF policy defines the system-account syscall allowlist for 32-bit x86 executor builds.

Important APIs and types: It exports `const struct sock_filter x86_system_filter[]` and `x86_system_filter_size`.

Control flow and state: The policy runs after syscall-number load and branches through generated `BPF_JGE` ranges and equality checks. It permits a broader i386 system syscall set than the restricted app policy, including privileged system-management ranges, while relying on the outer wrapper to trap unmatched syscalls. It has no mutable state.

Dependencies and integration points: It integrates through `android_seccomp.h` for `GOARCH_386` and `SCFS_SystemAccount`, with architecture validation and `prctl` installation handled there.

Risks and test signals: Risks include stale generated syscall ranges, wrong branch offsets, and accidental differences from Android’s canonical policy. Tests should compare with generated Android bionic output, compile on i386, install in an Android-like environment, and probe system-only and denied syscalls.
