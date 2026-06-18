# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fworm.c

Fake WORM device wrapper implemented on top of a writable backing device.

Key responsibilities:
- `fwormsize()` reserves trailing blocks as a bitmap, returning usable WORM blocks.
- `fwormream()` initializes trailing bitmap blocks with `Tvirgo` tags and zeros them.
- `fworminit()` initializes the backing device.
- `fwormread()` checks the bitmap bit before reading; unread/unwritten blocks return error.
- `fwormwrite()` checks the bitmap bit before writing; already-written blocks return error, new writes set the bit and write backing data.

Important interactions:
- Uses `FDEV(d)` as wrapped device.
- Uses `BUFSIZE*8` bits per bitmap block.
- Uses reserved buffer flag `Bres` when accessing bitmap blocks.

Research notes:
- This wrapper simulates write-once behavior by tracking written blocks in a bitmap stored at the end of the underlying device.
- Bounds checks panic if logical block numbers exceed fake-WORM usable size.
