# File Research: sources/os/linux/linux/fs/proc/consoles.c

## Purpose
Implements `/proc/consoles`, listing registered kernel consoles and their capabilities, flags, and device numbers.

## Main Responsibilities
- Iterates the console list through seq_file operations.
- Formats console name/index, read/write/unblank capabilities, console flags, and optional major/minor device.
- Serializes console device lookup with `console_lock()`.
- Protects list traversal with `console_list_lock()`.

## Key Interfaces
- `show_console_dev()`
- `consoles_op`
- `proc_consoles_init()`

## Control Flow and Data Handling
The seq start operation locks the console list and advances to the requested position. `show_console_dev()` builds a compact flag string from known `CON_*` bits and optionally asks the console for its backing tty driver/device index. Stop releases the console list lock.

## Dependencies and Integration
Depends on console core APIs, tty drivers, seq_file, and procfs creation.

## Risks and Review Hotspots
- Console list traversal requires correct lock pairing across seq start/stop.
- `con->device()` is serialized with `console_lock()` because console state such as foreground console can change.
- Output is consumed by diagnostics and should remain stable.
