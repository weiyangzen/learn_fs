# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiodev.h

Internal Ghostscript IODevice structure and procedure interface.

Key contents:
- Documents that IODevices are PostScript file/resource abstractions and distinct from Ghostscript output devices.
- Defines opaque references for file enumerators, parameter lists, and streams.
- Defines `gx_io_device_procs`, covering initialization, device/file stream opening, OS `FILE *` open/close, delete, rename, status, file enumeration, and parameter get/put hooks.
- Declares default no-op/error implementations and OS-backed `fopen`/`fclose` helpers.
- Declares IODevice lookup and parameter APIs: `gs_getiodevice`, `gs_findiodevice`, `gs_getdevparams`, and `gs_putdevparams`.
- Defines the concrete `gx_io_device` with name, type, procedure table, and optional state pointer.
- Provides a GC descriptor macro for IODevice state.

Notable dependencies:
- `stat_.h` for `struct stat`.
- Ghostscript memory, stream, and parameter types supplied by surrounding headers.

Research notes:
- This is the most file-abstraction-related file in the group: IODevices can return streams unrelated to the host OS filesystem.
- Some APIs take C strings while `open_file` and enumeration patterns include explicit lengths.
