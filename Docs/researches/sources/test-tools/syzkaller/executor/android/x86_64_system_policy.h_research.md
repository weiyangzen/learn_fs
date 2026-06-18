# sources/test-tools/syzkaller/executor/android/x86_64_system_policy.h

Purpose: This generated Android BPF policy defines the system-account syscall allowlist for x86_64 Android executor builds.

Important APIs and types: It exports `const struct sock_filter x86_64_system_filter[]` and `x86_64_system_filter_size`, consumed by `android_seccomp.h`.

Control flow and state: The filter executes after syscall number load and uses generated branch offsets to permit system-account ranges. Compared with app policy it includes privileged system operations such as module, syslog, reboot, mount/chroot-style groups where Android’s system policy allows them. There is no local persistence.

Dependencies and integration points: It depends on BPF/seccomp definitions and the outer wrapper for architecture validation, final trap, and installation.

Risks and test signals: Main risks are policy drift and accidental mismatch between x86_64 app/system arrays. Tests should include architecture-specific compilation, filter installation, representative system-only syscall probes, and generated-output diffing against Android bionic.
