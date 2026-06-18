<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2.c -->
# sources/test-tools/strace/tests/ioctl_v4l2.c

Purpose: Negative-path V4L2 ioctl decoder test. It verifies strace formatting for unknown V4L2 ioctl numbers, unsupported known commands, and many supported command argument shapes when syscalls fail with EBADF.

Important APIs/types/functions: Uses `ioctl`, `kernel_v4l2_types.h`, `kernel_fcntl.h`, V4L2 structures such as `v4l2_format`, `v4l2_fmtdesc`, `kernel_v4l2_buffer_t`, `v4l2_requestbuffers`, `v4l2_framebuffer`, `v4l2_streamparm`, `v4l2_control`, `v4l2_tuner`, `v4l2_queryctrl`, `v4l2_ext_controls`, `v4l2_frmsizeenum`, `v4l2_frmivalenum`, `v4l2_create_buffers`, `v4l2_exportbuffer`, and `v4l2_querymenu`. Helpers include `fourcc`, `init_v4l2_format`, `dprint_ioctl_v4l2`, and the `print_ioctl_v4l2` macro.

Control flow: The test allocates a filled page, brute-forces unknown `_IOC` values with V4L2 type `'V'` while skipping known VT/VBox conflicts, prints unsupported commands with raw arguments, then runs a long sequence of known commands with NULL, faulting, minimal, and filled structures. `init_v4l2_format` populates each buffer type union arm so `S_FMT` and `TRY_FMT` cover pix, multiplanar, overlay, VBI, sliced VBI, SDR, and metadata layouts.

State/persistence behavior: All calls use fd `-1`, so no video device is required and no kernel device state changes. State is deterministic in tail-allocated buffers, page-end fault probes, and compile-time xlat mode macros.

Dependencies: Requires the strace kernel V4L2 compatibility headers, ioctl and fcntl constants, endian conditionals, optional time32 buffer types, and xlat macros controlling raw/abbrev/verbose output.

Integration points: Tests the V4L2 ioctl decoder, fourcc rendering, nested union selection by `type`, flag and enum xlat rendering, output truncation for ext-control arrays, and behavior differences under `XLAT_RAW`, default abbreviated, and `XLAT_VERBOSE` builds.

Risks: V4L2 UAPI evolves quickly; new command numbers or enum values can change unknown/unsupported expectations. Structure layout and endian-dependent fourcc output are regression-prone. Because the test uses failed syscalls, the decoder must not treat all pointer arguments as successful output buffers.

Test signals: Expected output is large and includes unknown `_IOC` lines, supported command names, EBADF return markers, symbolic or raw xlat output according to wrapper mode, and `+++ exited with 0 +++`.

Source read signal: complete file read for this research pass; file size 1382 line(s), 48611 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2.c -->
