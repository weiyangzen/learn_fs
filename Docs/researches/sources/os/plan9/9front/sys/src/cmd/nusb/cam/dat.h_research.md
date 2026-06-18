# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/dat.h

This header defines the shared in-memory state used by the USB camera driver. `Format` pairs a UVC uncompressed-format descriptor with an array of frame descriptors. `VFrame` is the buffered video-frame object used by the streaming path, with byte count, allocation size, read cursor, data pointer, and linked-list pointer.

`Cam` is the main per-camera object. It stores the USB device and selected streaming endpoint, the streaming interface and input header, parsed format table, current UVC probe control, 9P file handles for camera files, and streaming state. The streaming fields include active/abort flags, active and free frame lists, a deferred-read request queue, a `QLock`, converter process id, and frame read mode.

The header also declares the global VideoControl unit arrays `nunit`, `unit`, and `unitif`, used by `ctl.c` and descriptor parsing code to associate UVC units with interfaces and advertised control bitmaps.
