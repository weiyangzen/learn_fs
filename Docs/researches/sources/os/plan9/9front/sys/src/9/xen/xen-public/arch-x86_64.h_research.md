# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_64.h

Imported Xen public 64-bit x86 compatibility include plus legacy callback note.

Purpose:
- Provides the legacy top-level 64-bit x86 public header path by including `arch-x86/xen.h`.
- Documents the older `HYPERVISOR_set_callbacks` 64-bit behavior.

Key content:
- Includes `arch-x86/xen.h`.
- Documents event and failsafe callback registration arguments and notes that selectors are ignored on x86-64.

Integration:
- Used for source compatibility with older Xen public header paths.
- The real x86-64 ABI definitions come through `arch-x86/xen.h` and `arch-x86/xen-x86_64.h`.

Risks/notes:
- Mostly forwarding/documentation, but callback semantics are relevant to low-level trap setup.
