# File Research: sources/os/plan9/9front/sys/src/9/port/rebootcmd.c

Kernel reboot command helper for rebooting into a loaded executable image.

Key responsibilities:
- With no arguments, moves the process to CPU0 and calls `exit(0)`.
- Opens the requested boot file with execute permission.
- Reads and validates the executable header.
- Supports additional header magic handling and architecture-specific text alignment.
- Allocates a text+data image, zero-fills it, reads text and data into place, sets `bootfile`, and calls `reboot(entry, image, size)`.

Important behavior:
- Uses big-endian header fields through `beswal()`.
- ARM64 `R_MAGIC` uses 64 KiB text segment alignment; others use page alignment.
- `readn()` treats zero-length reads before completion as `Eshort`.

Notable risks:
- Relies on architecture `reboot()` to consume the loaded image and transfer control.
