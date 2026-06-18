# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevimgn.c

Imagen ImPRESS printer driver.

Key behavior:
- Defines `imagen` printer device.
- Opens a multi-page ImPRESS document and closes with ImPRESS EOF, optionally byte-stream EOF.
- Supports 75/150/300 DPI through ImPRESS magnification.
- Converts raster pages into 32x32-bit ImPRESS swatches.
- Skips blank swatches and emits bitmap commands only for nonblank swatch runs.
- Optional byte-stream quoting handles quote/EOF/control characters.

Risks / notes:
- Uses environment variable `IMPRESSHEADER` to alter document header.
- Hardware assumptions are Canon CX/ImageStation oriented.
- Swatch copy optimization depends on `BIGTYPE` alignment and size assumptions.
