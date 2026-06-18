# File Research: sources/os/bsd/freebsd-src/sys/sys/slicer.h

Flash device slicing interface.

Key responsibilities:
- Defines maximum slice count, label length, read-only flag, and slice naming format.
- Defines `struct flash_slice` with base offset, size, label, and flags.
- Under kernel visibility, defines `flash_slicer_t` callback type.
- Defines flash slice provider types for NAND, CFI, SPI, and MMC.
- Declares `flash_register_slicer()` for registering or deregistering slicing callbacks.

Important patterns:
- A slicer callback fills an array of slice descriptors for a provider.
- Passing `NULL` with force is documented as the deregistration path.
- The interface abstracts partition-like fixed flash layouts outside conventional disk partition tables.

Research relevance:
- Small storage-adjacent header relevant to embedded flash-backed filesystem layouts.
