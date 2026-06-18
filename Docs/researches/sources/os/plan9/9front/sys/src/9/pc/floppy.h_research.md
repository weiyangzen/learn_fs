# File Research: sources/os/plan9/9front/sys/src/9/pc/floppy.h

Defines PC-specific floppy controller structures, register constants, setup functions, and small platform hooks for the generic floppy code.

Key elements:
- Declares generic floppy functions expected elsewhere: `floppyintr()`, `floppyon()`, `floppyoff()`, and `floppysetdef()`.
- `FDrive` records drive type, selected floppy format, device number, last access time, current cylinder, recalibration state, version, max retries, target CHS, transfer length, and a track cache.
- `FController` embeds a `QLock` for exclusive controller access and tracks drive array, selected drive, current data rate, command/status buffers, reset/confused state, rendezvous for command completion, and motor bitmask.
- `FType` describes a floppy media geometry and timing profile: sector size, sectors per track, heads, step rate, tracks, gaps, rate code, plus derived fields such as controller byte code, capacity, and track size.
- Defines I/O ports for PC floppy controller registers: status A/B, digital output, main status, data, disk-change input, and data-rate select.
- Defines command opcodes for recalibrate, seek, sense, read, read ID, specify, write, format, multi-head, and dump registers.
- Defines status bits for readiness, controller direction, busy state, disk change, seek completion, command execution, and overrun.
- `pcfloppyintr()` adapts the PC interrupt signature to the generic `floppyintr()`.
- `floppysetup0()` reserves floppy I/O port ranges and assumes up to two drives when reservation succeeds.
- `floppysetup1()` reads NVRAM equipment byte `0x10` to determine drive types, applies defaults, and enables IRQ `IrqFLOPPY`.
- `floppyeject()` powers the drive, bumps the drive version, and powers it off; the comment notes platform uncertainty.
- `floppyexec()` is a stub that returns the input byte count.

Filesystem relevance: direct but low-level. It supports the block-device side of floppy access by defining controller/drive geometry and PC I/O integration used by higher-level floppy device code.
