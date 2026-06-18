<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu.c

Purpose: KVM run variant focused on auxiliary fd string behavior when old kernels expose VCPU fds as `anon_inode:kvm-vcpu` without a `:0` suffix. It customizes the common test to print an explicit VCPU auxstr check.

Important APIs/types/functions: Defines `KVM_NO_CPUID_CALLBACK`, includes `ioctl_kvm_run_common.c`, and provides `print_KVM_RUN` plus a helper that formats expected `KVM_RUN` output with the current `vcpu_dev` string. It uses the same KVM ioctls and `struct kvm_run` data as the common test.

Control flow: common `main` detects whether `/proc/self/fd/<vcpu>` matches `anon_inode:kvm-vcpu:0`; if not, it trims the device string and invokes the callback. The variant's `print_KVM_RUN` checks the auxstr attached to VCPU fd output while the VM exit loop runs.

State and persistence behavior: transient VM/VCPU state only. The extra state is the mutable `vcpu_dev` expected-name buffer in common code.

Dependencies/integration points: integrates `/proc/self/fd` readlink behavior, strace fd auxstr rendering, and KVM `KVM_RUN` decoding.

Risks and test signals: kernel-version sensitive because VCPU fd names differ. The signal is stable expected output for `KVM_RUN` whether or not the kernel provides a CPUID suffix in the anon inode name.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu.c -->
