# File Research: sources/os/plan9/9front/sys/src/9/teg2/pciteg.c

Tegra 2 PCI/PCIe configuration-space access and scan setup.

Purpose:
- Provides Plan 9 PCI config read/write callbacks for Tegra 2/TrimSlice.
- Initializes PCI controller scanning and root device list.

Key behavior:
- Models Tegra PCI controller/port register layout and PCIe capabilities.
- `pcicfginit` verifies NVIDIA/Realtek presence, enables memory and bus-mastering, sets scanning limits, installs TBDF formatting, and scans bus 1 by default.
- `tegracfgaddr` maps TBDF/register offsets into Tegra config or extended config windows.
- `pcicfgrw8/16/32` implement config access; 32-bit reads probe the address first to avoid faults.
- `pcieintrdone` clears a magic AFI interrupt status register.

Filesystem relevance:
- Enables PCI-attached devices such as network/storage controllers that may host boot or file service paths.

Risks/notes:
- Comments say scanning beyond known buses can hang.
- Contains a Realtek interrupt hack and multiple board-specific assumptions.
