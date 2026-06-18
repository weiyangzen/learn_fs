# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-arm.h

Imported Xen public ARM architecture ABI header.

Purpose:
- Defines ARM Xen guest interface details for hypercalls, guest handles, vCPU register context, and PSR bits.

Key content:
- Documents ARM HVC hypercall calling convention and `XEN_HYPERCALL_TAG`.
- Defines ARM guest-handle unions and handle setters with 64-bit alignment rules.
- Defines `vcpu_guest_core_regs`, `vcpu_guest_context`, `arch_vcpu_info`, `arch_shared_info`, and callback type.
- Lists AArch32/AArch64 PSR mode values and interrupt/mode flags.

Integration:
- Part of Xen public ABI headers included or transformed for Plan 9 Xen support.

Risks/notes:
- ABI layout must remain compatible with Xen; local edits would risk hypercall/control-structure mismatch.
