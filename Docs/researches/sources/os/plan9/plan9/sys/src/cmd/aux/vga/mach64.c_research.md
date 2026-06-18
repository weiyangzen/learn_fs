# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64.c

Controller backend for ATI Mach64, modeled after the Mach32 backend.

Core behavior:
- Sets ATI extended register I/O address via graphics registers before using port `0x1CE`.
- Unlocks ATI extended register locks.
- Saves ATI extended registers plus Mach64 config/status/memory/scratch registers.
- Determines memory size from `Memcntl`.
- Assumes ATI18818 clock table and searches for a fixed clock within 1 MHz, including divide-by-two option.
- Programs 8-bit packed VGA-style mode, clock index bits, and interlace flag.
- Sets `ctlr->type = mach32.name`, making Mach64 reuse Mach32-style downstream behavior.
- Forces `vga->vmz` to 1 MB because Mach64 can only address 1 MB in VGA mode.

Ctlr:
- `mach64`

Notable risks:
- Header says no accelerator support and only up to 1024x768.
- Clock chip detection is not implemented; ATI18818 is assumed.
- Load path comments admit it does not fully ensure aperture/memory boundary/VGA-controller state.
