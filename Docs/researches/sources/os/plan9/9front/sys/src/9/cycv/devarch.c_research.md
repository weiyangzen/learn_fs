# File Research: sources/os/plan9/9front/sys/src/9/cycv/devarch.c

Cyclone V architecture device for FPGA configuration and arch control files.

Key responsibilities:
- Manages FPGA manager control/status/data registers.
- Waits for FPGA state transitions and interrupt completion.
- Streams FPGA bitstream data through a fixed buffer.
- Exposes arch device read/write/walk/stat/open/close operations.
- Initializes arch device directory entries and platform remap behavior.
- Provides attach support for the architecture device.

Important behavior:
- `fpgaconf()`, `fpgawrite()`, and `fpgafinish()` sequence FPGA configuration states.
- Uses timeout-based waits and an interrupt wake path.
- Write path is stateful across open/write/close.

Dependencies:
- Plan 9 device framework, FPGA manager registers, interrupt registration, reset/system manager registers, and kernel error handling.
