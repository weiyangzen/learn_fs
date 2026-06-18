# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevst.c

## Purpose
Implements the `%static%` IODevice for opening embedded static resources from `gs_init_string`.

## Key Functions
- `iostatic_init()` allocates IODevice state containing the static-resource dictionary.
- `iostatic_open_file()` resolves `%static%/category/instance` paths to offsets and returns a string-backed stream.
- `zsetup_io_static()` installs the resource dictionary into `%static%` device state.

## Important Behavior
- `%static%` paths must begin with `/category/instance`.
- Category and instance names are bounded by a local 30-byte buffer.
- Expects resource dictionaries to contain integer `StaticFilePos` and `StaticFileEnd`.
- Device state is GC-scannable because it stores a PostScript `ref`.

## Research Notes
Provides embedded-resource file access for startup/static resources, not host filesystem access.
