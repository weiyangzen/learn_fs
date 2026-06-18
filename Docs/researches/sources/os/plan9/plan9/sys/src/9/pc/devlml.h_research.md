# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlml.h

Read completely: 124 lines.

This header defines constants and DMA-visible data structures for the LML/Zoran Motion JPEG driver.

Key contents:
- Driver identity and sizing constants: `MJPG_VERSION`, `NLML`, `NBUF`, `FRAGSIZE`.
- Timeout and delay tunables for I2C, guest bus, and still capture polling.
- Zoran PCI identifiers and I2C addresses for BT819/BT856 companion chips.
- JPEG-like frame metadata structures:
  - `FrameHeader`
  - `Fragment`
  - `HdrFragment`
  - `FragmentTable`
  - `CodeData`

Important layout:
- Several structures are marked by comments as hardware-visible and should not be modified casually.
- `CodeData` contains physical pointers for the MJPEG status command area, grab buffer, fragment descriptors, and fragment buffers.
- `Codedatasize` and `Grabdatasize` are rounded to page size.

Research notes:
- The header assumes little-endian marker layout for SOI/APP3 markers.
- It is tightly coupled to `devlml.c`; no independent functions are defined here.
