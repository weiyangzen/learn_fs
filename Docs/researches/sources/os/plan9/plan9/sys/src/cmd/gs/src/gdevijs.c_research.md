# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevijs.c

Ghostscript IJS client device for driving external IJS printer servers such as hpijs.

Key behavior:
- Defines `ijs` printer device and `gx_device_ijs`.
- Starts an external server from `IjsServer`, opens an IJS job, passes output by filename or duplicated file descriptor.
- Negotiates generic params, duplex/tumble, paper size, printable area, top-left margins, resolution, color model, bits per sample.
- Has special compatibility paths for old hpijs 1.0 IJS version 0.29.
- Sends raster rows to IJS in `gsijs_output_page`, with hpijs white-row workaround.
- Parameter handling enforces `LockSafetyParams` for changing `IjsServer`.

Risks / notes:
- File itself warns that command-line selectable server executable is a security risk; `-dSAFER` is expected.
- `gsijs_read_string` writes `str[new_value.size+1] = '\0'`, which looks off by one for exact copied length.
- External process lifetime and error handling are central to reliability.
