# File Research: sources/os/plan9/plan9/sys/src/9/pc/floppy.h

PC floppy-controller declarations and PC-specific setup helpers. Despite the `.h` suffix, this file includes structure definitions, register/command constants, and small function bodies used by the floppy driver.

It declares `FDrive`, `FController`, and `FType`. `FDrive` stores selected media type, BIOS drive type, device number, last touched time, current cylinder, recalibration/confusion state, retry limit, target CHS/length for transfers, and track cache metadata. `FController` embeds a `QLock`, tracks up to four drives, selected drive, data rate, command/status buffers, reset/confusion state, command-completion rendezvous, and motor bitmask. `FType` describes media geometry and formatting parameters plus derived fields for controller byte-code, capacity, and track size.

The enum defines standard PC floppy I/O ports (`0x3f0`-`0x3f7`), digital output/input and main status bits, floppy commands such as recalibrate, seek, sense, read, read ID, specify, write, format, multi-head, dump registers, status-byte masks, and overrun bit.

`pcfloppyintr()` adapts the PC interrupt signature and calls the static driver-level `floppyintr()`. `floppysetup0()` reserves the floppy I/O port ranges and sets `ndrive=2` if successful. `floppysetup1()` reads NVRAM equipment byte `0x10`, extracts drive types for drives 0 and 1, calls `floppysetdef()`, and enables the floppy IRQ through `intrenable()`. `floppyeject()` powers the drive on, bumps its version, and powers it off; the comment says eject is unknown on Safari. `floppyexec()` is a stub that returns the byte count argument.

This header is tightly coupled to the surrounding floppy implementation through static forward declarations for `floppyintr`, `floppyon`, `floppyoff`, and `floppysetdef`. It also depends on PC I/O allocation, NVRAM, and interrupt APIs from `fns.h`.
