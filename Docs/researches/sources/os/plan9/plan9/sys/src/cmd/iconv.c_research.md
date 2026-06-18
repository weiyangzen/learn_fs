# File Research: sources/os/plan9/plan9/sys/src/cmd/iconv.c

`iconv.c` is an image channel converter for Plan 9 memory images.

Key behavior:
- Usage: `iconv [-u] [-c chanstr] [file]`.
- Reads a `Memimage` from stdin or a named file.
- Converts to requested channel descriptor via `allocmemimage` and `memimagedraw`.
- Writes compressed Plan 9 image output by default via `writememimage`.
- With `-u`, emits uncompressed image header plus raw scanlines from `unloadmemimage`.

Important dependencies:
- Uses `<draw.h>` and `<memdraw.h>` APIs.

Notable risks/quirks:
- Does not free image objects before exit, relying on process teardown.
- `writeuncompressed` validates exact scanline unload/write sizes and fatal-exits on mismatch.
