# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/elfnote.h

Imported Xen public ELF note definitions.

Purpose:
- Defines Xen-specific ELF note IDs used by Xen loaders, kernels, crash dumps, and dump-core tooling.

Key content:
- Documents PT_NOTE entries named `Xen`.
- Defines boot/kernel notes: info, entry, hypercall page, virtual base, physical-address offset, Xen version, guest OS/version, loader, PAE mode, feature strings, BSD symbol table, hypervisor start low, L1 MFN valid mask, suspend cancel, initial P2M location, module start PFN, supported feature bitmap.
- Defines `XEN_ELFNOTE_MAX`.
- Defines crash notes `XEN_ELFNOTE_CRASH_INFO` and `XEN_ELFNOTE_CRASH_REGS`.
- Defines dump-core notes for none/header/Xen version/format version.

Integration:
- Relevant to Xen boot image metadata rather than runtime I/O.
- Pairs with `features.h` for `XEN_ELFNOTE_FEATURES` and `XEN_ELFNOTE_SUPPORTED_FEATURES`.

Risks/notes:
- Loader-facing constants are ABI-stable; wrong note values can prevent boot or feature negotiation.
