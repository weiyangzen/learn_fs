# File Research: sources/os/bsd/netbsd-src/sys/sys/videoio.h

Read completely: 3419 lines.

Defines NetBSD's public V4L2-compatible video ioctl ABI. The file is an imported/adapted `videodev2.h` style header with inlined `v4l2-common.h` and `v4l2-controls.h` content, plus NetBSD ioctl encodings and kernel compatibility pieces.

Core API surface:
- Selection targets and flags cover crop/compose rectangles, defaults, bounds, native size, and legacy subdevice aliases.
- Control IDs span user controls, MPEG/codec controls, camera controls, FM TX/RX, flash, JPEG, image source/processing, DV, RF tuner, and detection classes.
- Core enums define fields, buffer types, tuner types, memory models, colorspaces, transfer functions, YCbCr/HSV encodings, quantization, and priority.
- Structs model V4L2 capabilities, pixel formats, frame size/rate enumeration, timecode, JPEG compression, streaming buffer/plane state, framebuffers/windows, stream parameters, crop/selection, analog standards, DV timings/capabilities, inputs/outputs, controls, tuners/modulators, frequency bands, RDS, audio, MPEG encoder/decoder commands, VBI formats, multi-plane/SDR formats, events, debug chip/register access, and buffer creation.

Format and ioctl coverage:
- Defines a large FOURCC catalog for RGB, greyscale, YUV packed/planar/multiplanar, Bayer, HSV, compressed, vendor-specific, SDR, and touch formats.
- Defines analog TV standard bitmasks and useful combined PAL/NTSC/SECAM/ATSC macros.
- Defines DV timing helpers for blanking/frame dimensions and packed BT.656/BT.1120 timing structs.
- `VIDIOC_*` ioctl constants cover capability query, format negotiation, buffer allocation/queue/dequeue/streaming, standards, inputs/outputs, controls, tuners, crop/selection, ext controls, frame enumeration, encoder/decoder commands, event subscription/dequeue, DV timings, frequency bands, debug register/chip info, and private ioctl range.
- Kernel-only compatibility defines `struct v4l2_buffer50` and `VIDIOC_QUERYBUF50`/`QBUF50`/`DQBUF50` for old timeval layout handling.

Integration notes:
- Uses NetBSD `sys/ioccom.h` `_IO*` macros while preserving Linux/V4L2 structure layouts and numeric constants as much as practical.
- Contains user-pointer fields marked with a local no-op `__user` when not otherwise defined.
- Includes `_KERNEL` conditional time compatibility for old timeval layouts.

Risks and notes:
- This is ABI material: structure packing, integer widths, pointer fields, and ioctl numbers must remain stable for userland and driver compatibility.
- The header intentionally mixes Linux-origin V4L2 semantics with NetBSD types; updates need careful cross-checking against both V4L2 upstream and NetBSD compat handling.
- Several APIs are explicitly deprecated or experimental but remain present for compatibility.
