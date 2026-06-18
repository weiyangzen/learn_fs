# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen.h

Imported Xen public common x86 guest ABI header.

Purpose:
- Provides x86-wide guest handle definitions, includes the correct 32/64-bit x86 ABI header, and defines shared x86 trap/vCPU/shared-info structures and constants.

Key content:
- Defines structural `XEN_GUEST_HANDLE` forms based on `__XEN_INTERFACE_VERSION__`.
- Selects `xen-x86_32.h` or `xen-x86_64.h` based on target architecture.
- Defines `xen_pfn_t`, `xen_ulong_t`, GDT reserved region constants, and `XEN_LEGACY_MAX_VCPUS`.
- Defines `struct trap_info` and helper macros for trap privilege and interrupt flags.
- Defines `struct vcpu_guest_context`, including FPU state, `VGCF_*` flags, CPU user registers, trap table, LDT/GDT, kernel stack, control/debug registers, callbacks, VM assist flags, and x86-64 segment bases.
- Defines `struct arch_shared_info` with max PFN, p2m list root, NMI reason, and padding.
- Defines `XEN_EMULATE_PREFIX` and `XEN_CPUID`.

Integration:
- Pulled in by compatibility wrappers `arch-x86_32.h` and `arch-x86_64.h`.
- The 9front Xen build’s `mkfile` includes x86 public headers when generating local Xen data/header material.
- Provides `vcpu_guest_context_t` and guest handles consumed by other public interfaces such as `domctl.h`.

Risks/notes:
- ABI-sensitive mixed 32/64 layout.
- Guest handle representation changes with interface version; generated headers and users must agree on `__XEN_INTERFACE_VERSION__`.
- Trap and vCPU context structures must match Xen exactly.
