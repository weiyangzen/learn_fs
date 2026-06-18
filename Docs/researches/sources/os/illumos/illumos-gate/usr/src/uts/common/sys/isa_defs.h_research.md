# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/isa_defs.h

This header defines architecture and data-model characteristics used throughout illumos headers.

Purpose:
- Centralizes processor characteristics and Solaris implementation choices for x86, amd64, and SPARC targets.
- Provides macros consumed by layout-sensitive headers such as InfiniBand management records and fixed-width integer headers.

Processor characteristic macros:
- Endianness: `_LITTLE_ENDIAN`, `_BIG_ENDIAN`.
- Stack growth direction.
- Long-long word order.
- Bitfield allocation order: `_BIT_FIELDS_LTOH` on x86/amd64, `_BIT_FIELDS_HTOL` on SPARC.
- IEEE 754 support.
- Char signedness.
- Primitive type alignment macros, `_MAX_ALIGNMENT`, `_MAX_ALIGNMENT_TYPE`, `_ALIGNMENT_REQUIRED`.
- Cache line shift/size.
- `_HAVE_CPUID_INSN` on x86.

Implementation choices:
- Data models: `_ILP32`, `_LP64`, `_MULTI_DATAMODEL`.
- VTOC form: `_SUNOS_VTOC_16` on x86, `_SUNOS_VTOC_8` on SPARC.
- DMA address model: physical on x86, virtual on SPARC.
- Firmware/fdisk/OBP/soft-hostid/platform module flags.
- Compatibility macro `__i386_COMPAT` for 32-bit ABI on amd64.
- Shared `__x86` and `__sparc` family macros.

Architecture branches:
- amd64/x86_64: LP64, little endian, 16-byte max alignment, physical DMA, fdisk, i386 compatibility.
- i386: ILP32, little endian, 4-byte max alignment, physical DMA.
- SPARC: big endian, high-to-low bitfields, virtual DMA, no fdisk, OBP; splits into SPARC V8 ILP32 and SPARC V9 LP64.
- Emits compile-time errors for unsupported ISA or both `_ILP32` and `_LP64`.

Relevance:
- Foundational ABI header. Many wire and ioctl layouts depend on these macros for correct cross-platform representation.
