# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiodev.h

Internal Ghostscript IODevice structure and procedure interface.

Key contents:
- Documents that IODevices are PostScript file/resource abstractions, distinct from Ghostscript output devices.
- Defines opaque references for file enumerators, parameter lists, and streams.
- Defines `gx_io_device_procs`, including initialization, opening device/file streams, OS `FILE *` open/close, delete, rename, status, file enumeration, and parameter get/put hooks.
- Declares default no-op/error implementations and OS-backed fopen/fclose helpers.
- Declares IODevice lookup and parameter APIs: `gs_getiodevice`, `gs_findiodevice`, `gs_getdevparams`, `gs_putdevparams`.
- Defines the concrete `gx_io_device` structure with name, type, procedure table, and implementation state pointer.
- Provides GC structure descriptor macro for IODevice state.

Notable dependencies:
- `stat_.h` for file status structure.
- Ghostscript memory, stream, and parameter types supplied by surrounding headers.

Research notes:
- This is one of the files in the group most directly related to file abstraction: IODevices may map names to non-OS-backed streams and do not need to implement OS `fopen`.
- File-name arguments for many procedures are C strings, while `open_file` and enumeration patterns carry explicit lengths.
