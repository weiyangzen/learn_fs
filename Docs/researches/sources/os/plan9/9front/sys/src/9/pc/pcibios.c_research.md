# File Research: sources/os/plan9/9front/sys/src/9/pc/pcibios.c

Implements PCI BIOS32-based PCI configuration access as a fallback or requested mode.

Key behavior:
- `pcibiosinit()` opens the BIOS32 `$PCI` service, issues PCI BIOS installation check function `0xB101`, verifies the returned signature, determines max device number and max bus number, and installs BIOS-backed config accessors.
- `pcicfgrw8bios()`, `pcicfgrw16bios()`, and `pcicfgrw32bios()` wrap PCI BIOS calls for byte/word/dword read and write.
- Read operations use BIOS function numbers `0xB108`, `0xB109`, and `0xB10A`.
- Write operations use `0xB10B`, `0xB10C`, and `0xB10D`.
- BIOS call registers encode bus/device/function in `ebx`, config register in `edi`, and data in `ecx`.

Research notes:
- `pcipc.c` calls `pcibiosinit()` when raw PCI config mechanisms are unavailable or `*pcibios` is set.
- On success, global function pointers `pcicfgrw8/16/32` are replaced so the rest of PCI code is agnostic to config-access method.
- The code ignores commented-out BIOS status checks on `ci.eax & 0xFF`, relying mainly on `bios32ci()` success.
