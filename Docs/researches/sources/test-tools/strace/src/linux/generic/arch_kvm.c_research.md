# sources/test-tools/strace/src/linux/generic/arch_kvm.c

Purpose: plugs `generic` into shared KVM ioctl/register decoding.

Important APIs/types/functions: arch_print_kvm_regs, arch_print_kvm_sregs; notable register references include none in this file.

Control flow: provides architecture-specific KVM helpers or includes a shared implementation so generic ioctl decoding can format VM/vCPU state.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on Linux KVM UAPI structs and strace's ioctl decoder.

Risks/test signals: stale KVM struct assumptions break ioctl formatting; test KVM_GET/SET ioctl traces.

Source-read signal: reviewed complete local file (26 lines).
