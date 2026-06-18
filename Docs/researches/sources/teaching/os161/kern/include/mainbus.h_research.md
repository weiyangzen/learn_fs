# File Research: sources/teaching/os161/kern/include/mainbus.h

Declares the machine-independent interface to the system bus layer.

Key APIs:
- Bootstrap/probe hardware.
- Start secondary CPUs.
- Dispatch bus-level interrupts.
- Report RAM size.
- Send low-level IPI.
- Enter debugger.
- Low-level halt, poweroff, reboot, and panic paths.

Relevance:
- Device discovery and shutdown infrastructure beneath block devices and mounted filesystems.
