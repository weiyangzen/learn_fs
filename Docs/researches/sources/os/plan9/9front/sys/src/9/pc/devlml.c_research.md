# File Research: sources/os/plan9/9front/sys/src/9/pc/devlml.c

LML33/Zoran Motion JPEG capture device driver implementing `#Λ`.

Key responsibilities:
- Probes up to two Zoran 36057/36067 PCI devices and allocates page-aligned shared capture metadata/buffers.
- Maps device registers and registers physical segments for MJPEG buffers and device registers.
- Initializes fragment descriptors and per-fragment JPEG APP3 frame headers.
- Exposes per-card control, JPEG, and raw frame files.
- Handles JPEG-repetition interrupts by finding completed buffers, stamping frame number/time/size/sequence metadata, and waking readers.

Important behavior:
- JPEG reads either return a full `FrameHeader` or a one-byte buffer number; raw reads use non-sleeping buffer polling.
- Only one JPEG/raw open is allowed per card.
- `lmlNctl` reports file names and physical segment ranges used for external mapping.

Dependencies:
- Depends on PCI, physical segment registration, Zoran/LML constants from `devlml.h`, MMIO mapping, interrupts, and `todget`.

Notable risks:
- Debug flags are enabled for read/write/filesystem categories by default.
- Buffer ownership depends on hardware-set `STAT_BIT` in shared memory.
