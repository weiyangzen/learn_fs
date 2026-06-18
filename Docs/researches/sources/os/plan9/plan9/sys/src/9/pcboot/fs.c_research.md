# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/fs.c

## Purpose
Generic boot filesystem adapter that walks paths and streams files into the kernel loader.

## Main Interfaces
- Exports `nextelem`, `fswalk`, `fsboot`, and `fsread`.

## Implementation Notes
- `nextelem` extracts slash/space-delimited path components into a fixed `NAMELEN` buffer.
- `fswalk` starts from `fs->root` and repeatedly calls the filesystem-specific `walk` method.
- `fsboot` walks to a file, allocates an 8 KiB buffer, reads through `fsread`, and feeds chunks to `bootpass`.
- End-of-file is signaled by `bootpass(b, nil, 0)` to attempt boot.
- `fsread` validates the `File` and filesystem read callback with `BADPTR`.

## Dependencies And Risks
- Path syntax is deliberately simple.
- Always returns `-1` after attempting to boot because successful boot does not return.
