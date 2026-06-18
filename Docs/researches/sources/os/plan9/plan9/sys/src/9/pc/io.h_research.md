# File Research: sources/os/plan9/plan9/sys/src/9/pc/io.h

- Size/hash: 384 lines, 9722 bytes, SHA-256 `f53f636f658d94947b04646ddcaee323db3757e3f52a91233bcd29bc6a445dd1`.
- Purpose: Shared PC I/O, interrupt, bus, PCI, SMBus, and PCMCIA definitions for the Plan 9 x86 kernel.
- CPU macros: `X86STEPPING`, `X86MODEL`, and `X86FAMILY` extract CPUID family/model data including extended bits.
- Interrupt model: Defines exception vectors, PIC vectors, LAPIC offsets, syscall vector 64, APIC vector range, IRQ constants, and `Vctl` interrupt-handler records.
- Bus encoding: Defines bus type enum and `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`, and `BUSUNKNOWN` macros for TBDF addressing.
- PCI definitions: Contains standard PCI config offsets, base/subclass constants, header-specific offsets, `Pcisiz`, `Pcidev`, common vendor IDs, and ISA/PCI address-window macros.
- SMBus/PCMCIA definitions: Defines SMBus transaction enum and `SMBus`; defines `PCMmap`, `PCMconftab`, and `PCMslot` structures for PCMCIA slot/configuration state.
- Dependencies: References Plan 9 kernel types such as `Lock`, `QLock`, `Rendez`, `Pcidev`, `Ureg`, and `KNAMELEN`.
- Research notes: This is a hardware interface contract header. Storage drivers use these definitions for PCI discovery, IRQ registration, and bus/device addressing.
