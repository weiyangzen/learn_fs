# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodev.c

Implements Ghostscript IODevice dispatch and the `%os%` filesystem device.

Startup:
- Imports configured IODevice table.
- `gs_iodev_init` allocates writable GC-tracked copies of every configured IODevice and runs each device init procedure.
- Registers `io_device_table` as a structure root.

Default procedures:
- Provides `iodev_no_*` implementations returning invalid access, undefined filename, IO error, or no-op parameter behavior.

`%os%` device:
- Uses `gp_fopen`, `fclose`, `unlink`, `rename`, `stat`, and platform enumeration wrappers.
- `os_get_params` returns generic filesystem parameters with fake block/free/logical-size values.

Utilities:
- `gs_getiodevice`
- `gs_findiodevice`
- `gs_getdevparams`
- `gs_putdevparams`
- `gs_fopen_errno_to_code`

Risks and quirks:
- Failure cleanup in `gs_iodev_init` has suspicious indexing (`table[i - 1]`) and a comment that unregistering the root is unresolved.
- Capacity reporting is intentionally fake and platform-independent.
