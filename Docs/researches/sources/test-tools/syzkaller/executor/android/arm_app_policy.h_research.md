# sources/test-tools/syzkaller/executor/android/arm_app_policy.h

Purpose: This generated Android BPF policy defines the restricted app syscall allowlist for 32-bit ARM. It supports Android sandboxing for `GOARCH_arm`.

Important APIs and types: It exports `const struct sock_filter arm_app_filter[]` and `arm_app_filter_size`. The filter contains a larger 32-bit syscall-number decision tree than arm64 because ARM exposes legacy syscall numbers and ABI-specific calls.

Control flow and state: After `android_seccomp.h` loads `seccomp_data.nr`, this filter compares numeric syscall ranges with `BPF_JGE` and specific equality checks such as futex and ioctl. The comments list allowed legacy and modern calls, including old 32-bit file/stat variants, socket operations, scheduler/timer calls, xattr, epoll, pidfd, clone3, close_range, and process_madvise ranges. It contains no writable state.

Dependencies and integration points: It relies on classic BPF macros and the Android-generated syscall list. The wrapper provides architecture validation for `AUDIT_ARCH_ARM`, final trap behavior, and installation.

Risks and test signals: 32-bit ARM policy is especially sensitive to legacy syscall numbering and Android bionic generator changes. Tests should compile for ARM, compare generated output against Android source, cover pthread creation requirements, and validate representative legacy syscalls plus a denied syscall path.
