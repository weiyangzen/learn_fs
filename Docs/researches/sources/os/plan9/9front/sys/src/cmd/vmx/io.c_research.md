# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/io.c

This file implements most legacy PC I/O-port devices and central I/O dispatch.

Key behavior:
- Emulates CMOS/RTC, including memory-size initialization, BCD time fields, periodic interrupt timing, and IRQ8 updates.
- Emulates dual 8259 PICs, IRQ lines, acknowledge, ELCR edge/level mode, ICW/OCW programming, priority, mask, poll, and automatic EOI.
- Emulates PIT channels and port 0x61 speaker latch enough for timers and IRQ0.
- Emulates i8042 keyboard/mouse controller, keyboard command ACKs, PS/2 mouse modes, packet generation, IntelliMouse detection sequence, IRQ1/IRQ12, and reset pulses.
- Emulates two UARTs with optional file-backed input/output processes and IRQ generation.
- Provides a dummy floppy controller and several no-op legacy port ranges used by probes/delays.
- `handlers` maps fixed port ranges; `io0` falls through to PCI I/O BARs; `io` masks transfer sizes and optional per-port debug logging.

Integration and risks:
- Device emulation is intentionally partial but tuned for guest OS boot/probing.
- Timer and interrupt behavior depends on `nanosec`, `settimer`, and VM state transitions.
- Keyboard/mouse channels are shared with `vga.c`.
