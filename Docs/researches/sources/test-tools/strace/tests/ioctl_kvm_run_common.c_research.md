<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_common.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run_common.c

Purpose: shared implementation for KVM ioctl decoding tests. It builds a tiny x86 guest, drives real KVM ioctls, and prints expected strace output for VM creation, memory mapping, register setup, CPUID handling, and `KVM_RUN` exits.

Important APIs/types/functions: Uses `kvm_ioctl`/`KVM_IOCTL`, `print_kvm_segment`, `print_kvm_sregs`, `print_kvm_regs`, `run_kvm`, `vcpu_dev_should_have_cpuid`, and `print_cpuid_ioctl`. Key UAPI types are `kvm_userspace_memory_region`, `kvm_sregs`, `kvm_regs`, `kvm_run`, `kvm_cpuid2`, and `kvm_cpuid_entry2`.

Control flow: `main` checks `/proc/self/fd`, opens `/dev/kvm`, verifies API version and memory capability, creates VM and VCPU, maps guest memory to page frame one, maps the VCPU run page, probes supported CPUID, sets CPUID twice, tests EFAULT for NULL CPUID, then calls `run_kvm`. `run_kvm` reads/modifies segment registers, sets general registers, copies the embedded real-mode assembly, repeatedly calls `KVM_RUN`, validates IO/MMIO/HLT exits, and calls variant-provided `print_KVM_RUN`.

State and persistence behavior: maintains page size, expected device strings, anonymous guest memory, mmaped shared `kvm_run` state, and kernel VM/VCPU objects. It intentionally mutates `run->mmio.data[0]` before a read continuation so strace can decode before-state data. Nothing persists after process exit.

Dependencies/integration points: gated on KVM headers, specific structs, and x86. Depends on `/dev/kvm`, mmap, `/proc/self/fd`, xlat CPUID flags, and optional macro hooks `VERBOSE`, `KVM_NO_CPUID_CALLBACK`, and variant `print_KVM_RUN`.

Risks and test signals: high environmental risk from missing KVM, permissions, nested virtualization, or kernel naming differences. Test signal is exact stdout plus skip behavior; failures expose KVM ioctl decoder regressions, auxstr mismatches, or changed VM exit semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_common.c -->
