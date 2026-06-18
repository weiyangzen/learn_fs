# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.c

Generic USB serial file server and common serial control layer.

Main responsibilities:
- Exposes each serial interface as a `Usbfs` subtree with data and control files, usually `eiaU*` and `eiaU*ctl`, plus JTAG naming for JTAG interfaces.
- Parses control commands in `serialctl`: baud, line bits, parity, stop bits, RTS/DTR/modem, break, flush, software flow characters, and other Plan 9 serial controls.
- Provides `serdumpst` status formatting for control reads.
- Opens bulk IN/OUT and optional interrupt endpoints with timeouts and chip-specific endpoint setup.
- `dread` serves directory reads, data reads, and control status reads.
- `dwrite` writes serial data or applies control commands.
- `altwrite` handles data writes with timeout retry and recovery.
- `serialrecover` un-stalls endpoints, resets devices, or detaches after repeated failures.
- `serialreset` drains ports and invokes chip reset hooks.
- `serialmain` detects chip backend, initializes interfaces, starts per-interface file systems, and registers them under `usbdirfs`.

Backend integration:
- Uses `Serialops` installed from Prolific, ucons, FTDI, or Silabs.
- Supports chip-specific `wait4data`, `wait4write`, `setparam`, `sendlines`, `setbreak`, and recovery hooks.

Risks/quirks:
- Some error-run counters are static in `dread`, not per port.
- Long continuous read errors can terminate all serial service.
- Comments note software flow control is not fully implemented.
