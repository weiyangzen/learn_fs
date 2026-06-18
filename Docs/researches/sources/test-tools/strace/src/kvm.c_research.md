# sources/test-tools/strace/src/kvm.c

Purpose: decodes KVM ioctls, tracks vCPU file descriptors, and optionally prints `struct kvm_run` exit state.

Important APIs/types/functions: `kvm_ioctl`, `kvm_vcpu_info_free`, `vcpu_find`, `vcpu_register`, `vcpu_get_info`, `kvm_ioctl_create_vcpu`, decoders for memory regions, regs, sregs, CPUID, check-extension, run, `kvm_run_structure_decode`, `kvm_run_structure_decoder_init`, `decode_kvm_run_structure`, and arch hooks from `arch_kvm.c`.

Control flow: `kvm_ioctl` dispatches by ioctl code. Creating a vCPU prints cpuid and, on successful exit, records returned fd. Memory, register, sreg, and CPUID ioctls decode pointed-to structures with get/set entry/exit direction. `KVM_RUN` optionally snapshots the `kvm_run` mmap on entry, decodes exit reason on successful exit, and later prints before/after run structures including IO/MMIO union details.

State and persistence behavior: maintains a per-tracee linked list of `vcpu_info` records in `tcb`, including fd, cpuid, mmap address/length, and resolution status. Uses mmap cache to find anon-inode vCPU mappings and stores entering/leaving run snapshots. `kvm_vcpu_info_free` releases this state.

Dependencies and integration points: compiled under `HAVE_LINUX_KVM_H`; depends on Linux KVM headers, architecture-specific KVM printers, mmap cache, fd path resolution, xlat tables for exits, IO directions, caps, CPUID flags, and memory flags.

Risks: vCPU mapping discovery depends on anon-inode path names and mmap cache freshness. `struct kvm_run` decoding is gated by runtime mode and may be unavailable if mmap cannot be resolved. Static storage in exit auxiliary decoding is reused per call.

Test signals: cover KVM_CREATE_VM/CREATE_VCPU fd returns, vCPU registration, KVM_SET_USER_MEMORY_REGION, regs/sregs get/set phase behavior, CPUID arrays with abbrev/non-abbrev output, KVM_CHECK_EXTENSION xlat, KVM_RUN exit reason, IO/MMIO union decoding, mmap remap handling, and cleanup of tracked vCPUs.
