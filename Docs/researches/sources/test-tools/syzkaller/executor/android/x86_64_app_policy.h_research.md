# sources/test-tools/syzkaller/executor/android/x86_64_app_policy.h

Purpose: This generated Android BPF policy defines the restricted app syscall allowlist for x86_64 Android executor builds.

Important APIs and types: It exports `const struct sock_filter x86_64_app_filter[]` and `x86_64_app_filter_size`. The decision tree allows selected x86_64 syscall numbers and ends in an allow return for matched paths.

Control flow and state: The wrapper loads the syscall number and this policy applies range/equality checks. Comments show app-allowed groups such as read/write/open/close, mmap/mprotect, signal/timer/scheduler, sockets, xattr, epoll, process_vm, seccomp, bpf, pidfd, clone3, close_range, and process_madvise. The policy itself has no mutable state.

Dependencies and integration points: It is included by `android_seccomp.h` under `GOARCH_amd64`, paired with `AUDIT_ARCH_X86_64`, and installed through the common filter assembly path.

Risks and test signals: x86_64 app policy includes additional pthread-related syscalls noted in the wrapper, so stale generation can break executor threading. Tests should verify `clone3`, robust-list behavior, futex, ioctl, and denial behavior, and compare against Android bionic generation for x86_64.
