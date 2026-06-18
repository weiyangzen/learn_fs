# File Research: sources/virtualization/qemu/tools/qemu-vnc/chardev.c

## Purpose
Discovers QEMU D-Bus chardev objects and exposes selected character devices as VNC text consoles.

## Behavior
- Defaults to chardev names:
  - `org.qemu.console.serial.0`
  - `org.qemu.monitor.hmp.0`
- Allows caller-provided chardev name list.
- For matching `org.qemu.Display1.Chardev` objects, creates a Unix socketpair.
- Passes one fd to QEMU through `Register`.
- Creates a local `QemuTextConsole` for the other fd after registration succeeds.
- Reads optional `org.qemu.Display1.Chardev.VCEncoding` to set text encoding.

## Error Handling
- Failed registration closes the local fd.
- Failed text console creation also closes the local fd.
- Unknown or unmatched chardevs are ignored.

## Filesystem/Storage Relevance
Indirect. This exposes monitor/serial channels over VNC, which may be used for VM management but is not filesystem-specific.
