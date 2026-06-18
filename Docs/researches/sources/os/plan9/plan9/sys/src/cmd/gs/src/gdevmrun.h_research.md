# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.h

Definition of the run-length encoded memory-device wrapper.

- Includes `gxdevmem.h` and defines `gx_device_run`.
- `gx_device_run` embeds `gx_device_memory md` as its first field for device compatibility.
- Tracks run capacity per line, an uninitialized line range, and a standard/uncompressed line range.
- Stores saved memory-device procs for copy mono/color, fill rectangle, copy alpha, strip tile, strip copy ROP, and get-bits rectangle.
- Declares `gdev_run_from_mem(gx_device_run *rdev, gx_device_memory *mdev)`.
- Intended behavior: use RLE storage when useful and fall back to standard bitmap representation as needed.
