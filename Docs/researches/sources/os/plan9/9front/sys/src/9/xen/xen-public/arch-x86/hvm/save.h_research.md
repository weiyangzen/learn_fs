# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/hvm/save.h

Imported Xen public x86 HVM save-state ABI definitions.

Purpose:
- Defines structures and save-type records used by Xen to save/restore HVM domain CPU and device-model state.

Key content:
- Save file magic/version and `hvm_save_header`.
- CPU register/control/debug/MSR/FPU state structures, including compatibility forms.
- Device-state structures for vPIC, vIOAPIC, LAPIC, PCI IRQ routing, ISA IRQs, PIT, RTC, HPET, PM timer, MTRR, XSAVE, Viridian, VMCE, and TSC adjust.
- Defines save type codes and maximum code.

Integration:
- Public ABI reference in Xen header tree; not directly part of Plan 9 filesystem logic but supports virtualization interface completeness.

Risks/notes:
- Struct packing/layout must track Xen ABI exactly.
