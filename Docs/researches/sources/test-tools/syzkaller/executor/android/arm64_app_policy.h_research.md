# sources/test-tools/syzkaller/executor/android/arm64_app_policy.h

Purpose: This generated Android BPF policy defines the allowed syscall set for restricted app accounts on AArch64. It is included by `android_seccomp.h` when `GOARCH_arm64` is selected.

Important APIs and types: It exports `const struct sock_filter arm64_app_filter[]` and `arm64_app_filter_size`. The array is a decision tree of `BPF_JUMP` range/equality checks over syscall numbers followed by `BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ALLOW)` for allowed paths; the wrapper appends a trap fallback.

Control flow and state: The filter assumes the syscall number is already loaded into the BPF accumulator by `ExamineSyscall`. The generated tree uses `BPF_JGE` ranges and occasional `BPF_JEQ` fast paths for important syscalls such as futex and ioctl. Comments document contiguous allowed syscall names for each range. The header has no mutable state.

Dependencies and integration points: It depends on Linux classic BPF macros and Android’s generated syscall policy source. `android_seccomp.h` adds architecture validation and installation.

Risks and test signals: Since syscall numbers and Android policy evolve, stale generated content can deny required libc/runtime calls or allow calls Android no longer permits. App policy includes process, file, memory, signal, socket, and newer pidfd/syscall ranges through the generated tree. Tests should compare against current Android bionic generation, install on arm64, validate pthread/futex/ioctl paths, and confirm non-listed syscalls hit the appended trap.
