# sources/test-tools/strace/src/linux/x32/arch_kvm.c

## Purpose
Reuses x86_64 KVM register and segment decoding for the x32 target.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_kvm.c`, which conditionally defines `arch_print_kvm_regs`, segment/dtable helpers, and `arch_print_kvm_sregs` when the relevant KVM structs are available.

## Control Flow and Integration
The inherited code prints KVM general registers, special registers, segment descriptors, descriptor tables, control registers, EFER, APIC base, and interrupt bitmap. It respects `abbrev(tcp)` by shortening output.

## State and Persistence
No persistence. It reads already-fetched KVM ioctl structures and writes decoded output.

## Dependencies
Depends on Linux KVM structure definitions and generic ioctl/KVM decoding. x32 uses x86 KVM ABI layouts, so the x86_64 implementation is shared.

## Risks
KVM ioctl structure sizes differ between 32-bit and 64-bit contexts for some commands. This include is appropriate for x32's x86_64 kernel-facing KVM structs but must be checked when KVM headers change.

## Test Signals
KVM ioctl tests on x32 should verify `KVM_GET_REGS`, `KVM_SET_REGS`, `KVM_GET_SREGS`, and abbreviated output.
