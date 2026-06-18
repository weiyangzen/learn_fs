<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run.c

Purpose: base KVM run test wrapper. It includes `ioctl_kvm_run_common.c` with default abbreviated formatting to exercise real `/dev/kvm` ioctl decoding and `KVM_RUN` exit rendering.

Important APIs/types/functions: The implementation is in the included common file: `KVM_GET_API_VERSION`, `KVM_CHECK_EXTENSION`, `KVM_CREATE_VM`, `KVM_SET_USER_MEMORY_REGION`, `KVM_CREATE_VCPU`, `KVM_GET_VCPU_MMAP_SIZE`, `KVM_GET/SET_SREGS`, `KVM_SET_REGS`, `KVM_GET_SUPPORTED_CPUID`, `KVM_SET_CPUID2`, and `KVM_RUN`.

Control flow: compile-time inclusion supplies `main`. At runtime it opens `/dev/kvm`, creates a VM/VCPU, maps guest memory and the `kvm_run` area, configures CPUID and registers, copies a tiny x86 real-mode program, and loops through KVM exits until HLT.

State and persistence behavior: all state is transient kernel KVM state plus anonymous memory mappings. The test verifies state transitions visible through ioctls, not disk persistence.

Dependencies/integration points: requires Linux KVM UAPI, x86, accessible `/dev/kvm`, mmap, and strace fd-path decoding. It is skipped when prerequisites or compatible kernel features are absent.

Risks and test signals: environment-sensitive because KVM availability and permissions vary. Passing output confirms abbreviated decoding of KVM setup ioctls, CPUID arrays, register structs, and `KVM_RUN` exit data.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run.c -->
