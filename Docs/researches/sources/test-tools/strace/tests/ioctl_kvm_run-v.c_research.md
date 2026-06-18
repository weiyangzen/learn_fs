<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run-v.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run-v.c

Purpose: verbose-mode variant of the KVM run test. It defines `VERBOSE 1` before including `ioctl_kvm_run.c`, expanding register, segment, CPUID, and `kvm_run` structure output beyond the abbreviated base mode.

Important APIs/types/functions: Inherits all KVM APIs from `ioctl_kvm_run_common.c`, especially `/dev/kvm`, `KVM_GET_*`, `KVM_SET_*`, `KVM_RUN`, `struct kvm_regs`, `kvm_sregs`, `kvm_cpuid2`, and `kvm_run`. The local API surface is only the compile-time `VERBOSE` macro.

Control flow: compilation routes through `ioctl_kvm_run.c` into the common implementation; runtime is identical to the base KVM test but all `#if VERBOSE` branches print full segment registers, all general registers, CPUID entries, and richer exit payload fields.

State and persistence behavior: creates a transient VM, VCPU, mmaped guest page, and `kvm_run` mapping. No durable state is written; verbose mode changes only expected trace text.

Dependencies/integration points: requires KVM headers, x86, `/dev/kvm`, and `/proc/self/fd`. Integrates with strace verbose decoder output contracts.

Risks and test signals: verbose expected output is more sensitive to kernel-provided CPUID and register layouts. Passing output confirms strace can print non-abbreviated KVM ioctl structures and exits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run-v.c -->
