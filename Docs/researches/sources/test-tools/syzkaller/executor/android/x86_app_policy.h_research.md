# sources/test-tools/syzkaller/executor/android/x86_app_policy.h

Purpose: This generated Android BPF policy defines the restricted app syscall allowlist for 32-bit x86 (`GOARCH_386`) executor builds.

Important APIs and types: It exports `const struct sock_filter x86_app_filter[]` and `x86_app_filter_size`. The filter is a classic BPF syscall decision tree with comments mapping numeric ranges to syscall names.

Control flow and state: `android_seccomp.h` loads `seccomp_data.nr`, then this tree handles legacy i386 syscall numbering including `socketcall`, old stat/file operations, xattr, epoll, pidfd, clone3, close_range, and process_madvise ranges. Matching paths return `SECCOMP_RET_ALLOW`; the wrapper appends trap on fallthrough. No state is stored.

Dependencies and integration points: It is selected under `GOARCH_386` and paired with `AUDIT_ARCH_I386` by the Android seccomp wrapper.

Risks and test signals: The 32-bit x86 ABI has many legacy multiplexed or obsolete syscalls, so policy drift can produce surprising executor failures. Tests should cover i386 compilation, BPF verifier acceptance, `socketcall` behavior, pthread requirements, and negative probes for denied syscalls.
