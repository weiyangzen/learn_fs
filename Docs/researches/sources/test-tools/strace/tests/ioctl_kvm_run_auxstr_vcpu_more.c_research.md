<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu_more.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu_more.c

Purpose: extension of the VCPU auxstr KVM run variant that adds a `print_KVM_RUN_MORE` hook for additional `kvm_run` exit detail checks.

Important APIs/types/functions: Defines `print_KVM_RUN_MORE` before including `ioctl_kvm_run_auxstr_vcpu.c`, then implements extra printing functions after inclusion. It depends on `struct kvm_run`, KVM exit fields, and the same `vcpu_dev`/fd auxstr paths as the included variant.

Control flow: included common code performs VM setup and the exit loop. When `print_KVM_RUN` is called, this variant's extra hook observes before/after `kvm_run` data and prints additional expected fragments for IO/MMIO exit decoding.

State and persistence behavior: transient KVM and memory-mapped state only. The additional hook consumes snapshots of the shared `kvm_run` mapping captured before each `KVM_RUN`.

Dependencies/integration points: tests the integration between KVM exit data, strace's auxstr fd formatting, and macro-injected expected-output helpers.

Risks and test signals: sensitive to exact exit sequence from the embedded x86 program. Passing output confirms that richer VCPU auxstr/exit rendering remains stable under the specialized variant.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu_more.c -->
