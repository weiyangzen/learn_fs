# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodev.c

## Role

`gsiodev.c` implements core Ghostscript IODevice registration, default unimplemented device procedures, the `%os%` host filesystem IODevice, IODevice lookup/accessors, and OS-error to PostScript-error mapping.

This is Ghostscript IO abstraction code with host filesystem access, not a filesystem implementation.

## Main Interfaces

- Initialization: `gs_iodev_init`.
- Default operations: `iodev_no_init`, `iodev_no_open_device`, `iodev_no_open_file`, `iodev_no_fopen`, `iodev_no_fclose`, `iodev_no_delete_file`, `iodev_no_rename_file`, `iodev_no_file_status`, `iodev_no_enumerate_files`, `iodev_no_get_params`, `iodev_no_put_params`.
- `%os%` operations: `iodev_os_fopen`, `iodev_os_fclose`, `os_delete`, `os_rename`, `os_status`, `os_enumerate`, `os_get_params`.
- Utilities: `gs_getiodevice`, `gs_findiodevice`, `gs_getdevparams`, `gs_putdevparams`, `gs_fopen_errno_to_code`.

## Core Behavior

- At startup, copies each configured IODevice into writable GC-managed structures and registers the device table as a GC root.
- `%os%` delegates opening to `gp_fopen`, closing to `fclose`, deletion to `unlink`, renaming to `rename`, status to `stat`, and enumeration to `gp_enumerate_files_*`.
- `%os%` reports generic/fake capacity parameters such as 1 KB block size and roughly 2 GB logical size.
- `gs_findiodevice` accepts both `%device` and `%device%` spellings.
- `gs_fopen_errno_to_code` maps common `errno` values to Ghostscript/PostScript errors.

## Notable Risks

- The failure cleanup loop in `gs_iodev_init` uses `table[i - 1]` while iterating down from `i`, which is a fragile legacy pattern and looks problematic when `i == 0`.
- `%os%` performs real host filesystem operations directly through platform wrappers; policy/sandboxing must happen elsewhere.
- `iodev_os_fopen` copies `fname` to `rfname` with `strcpy` if buffers differ, trusting the caller-provided buffer size.
- Device capacity reporting is explicitly fake and platform-independent rather than accurate.
