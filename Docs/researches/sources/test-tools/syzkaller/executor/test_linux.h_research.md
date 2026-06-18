# sources/test-tools/syzkaller/executor/test_linux.h

Purpose: Linux-specific executor self-tests for KVM setup and SYZOS installation.

Important APIs and control flow: `test_one` creates `/dev/kvm` VM/VCPU, maps `kvm_run`, allocates guest memory, calls `syz_kvm_setup_cpu`, runs `KVM_RUN`, checks exit reason, and optionally verifies result register (`rax` on amd64, `gpr[3]` on ppc64le). `test_kvm` chooses architecture-specific guest byte snippets and setup flags; amd64 gates VMX cases on supported CPUID and SMM cases on kernel version, while ppc64le loops flag combinations for generated snippets. `host_kernel_version`, `dump_cpu_state`, `dump_seg`, and `cpu_feature_enabled` support diagnostics. `test_syzos` on arm64 maps memory and calls `install_syzos_code`.

State and dependencies: uses real KVM fds, guest memory, generated KVM blobs, and setup helpers outside this subset. It prints detailed CPU state on failure.

Integration points: included by `test.h` for Linux amd64/ppc64/ppc64le/arm64. Validates `kvm.h`, generated assembly headers, and KVM pseudo-syscall setup.

Risks and tests: failures can be environmental (`/dev/kvm` absent, permissions, unsupported CPU feature) and return SKIP where appropriate. Hardcoded expected exit reasons vary by setup mode and architecture.
