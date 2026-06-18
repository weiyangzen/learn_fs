# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/dat.h

This is the shared VMX data-model header for memory regions, PCI devices, VGA modes, interrupts, and x86 access helpers.

Key contents:
- Defines VM states, register-name macros, page size, MMIO operation constants, and IRQ special values.
- `Region` describes guest physical mappings, permissions, optional segment backing, BIOS/E820 type, and MMIO callbacks.
- `PCIDev`, `PCIBar`, and `PCICap` model simple PCI config space, BARs, caps, and IRQ state.
- `VgaMode` describes framebuffer modes.
- `TLB` caches recent guest x86 memory translation/access state.
- Declares shared globals such as `mmap`, `state`, `debug`, `irqactive`, `cmos`, and `kconfig`.

Integration and risks:
- Many implementation files share these structs directly, so layout changes ripple widely.
- E820 region type is encoded in the high bits of `Region.type`.
