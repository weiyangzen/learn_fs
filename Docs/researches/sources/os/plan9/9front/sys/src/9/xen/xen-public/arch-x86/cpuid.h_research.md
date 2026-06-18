# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/cpuid.h

Imported Xen public x86 CPUID interface definitions.

Purpose:
- Defines Xen identification CPUID leaves and feature flags.

Key content:
- Xen CPUID leaf base `0x40000000` and `XEN_CPUID_LEAF`.
- Signature values for `XenVMMXenVMM`.
- Documents version and feature leaves.
- Defines feature bit for `MMU_PT_UPDATE_PRESERVE_AD`.

Integration:
- Used by Xen-aware x86 code to detect/paraphrase hypervisor capabilities.

Risks/notes:
- Pure ABI header; values are externally defined by Xen.
