<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success.c

Purpose: Injected-success V4L2 ioctl decoder test. It exercises output-argument and bidirectional-argument formatting for many V4L2 structs without depending on a real video device.

Important APIs/types/functions: Uses `ioctl`, `strtoul`/`strtol` for fault-injection lock-on arguments, V4L2 structs from `kernel_v4l2_types.h`, `fill_fmt`, `print_fmt`, and optional `test_v4l2_buffer_time32`. It covers `VIDIOC_QUERYCAP`, `VIDIOC_ENUM_FMT`, `VIDIOC_REQBUFS`, `VIDIOC_EXPBUF`, `VIDIOC_G/S/TRY_FMT`, buffer queue ioctls, framebuffer, stream parameters, standards, inputs, controls, tuners, crop, frame sizes/intervals, create buffers, extended control queries, and menu queries.

Control flow: `main` exits silently if run without injection parameters, otherwise it loops over `VIDIOC_QUERYCAP` until strace fault injection returns the requested non-negative value. After lock-on, it populates structures with deterministic patterns and issues each ioctl against fd `-1`; expected output appends `(INJECTED)` and includes decoded output fields as if the calls succeeded.

State/persistence behavior: No real video state is touched because fd `-1` and injected return values drive the success path. State is the filled structure memory, persistent static clip storage in `fill_fmt`, and output formatting controlled by compile-time `VERBOSE` and `XLAT_*` macros.

Dependencies: Requires strace fault-injection harness, V4L2 compatibility types, fcntl flag constants, optional time32 structures, and xlat mode macros. The executable must receive `NUM_SKIP INJECT_RETVAL`.

Integration points: Validates success-path ioctl decoding for nested structures, output updates, decoded capabilities, controls, buffer flags, timestamps, frame intervals, query dimensions, fourcc names, and verbose-only reserved fields.

Risks: Large combinatorial coverage means UAPI additions, enum renames, or struct layout changes can ripple through expected output. Injection lock-on must stay aligned with test driver options; otherwise the test fails before the decoder logic runs.

Test signals: Look for an initial injected `VIDIOC_QUERYCAP` lock line, decoded structures with `= <retval> (INJECTED)`, optional verbose reserved fields, raw/abbrev/verbose xlat differences, and the final exit marker.

Source read signal: complete file read for this research pass; file size 1768 line(s), 61755 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success.c -->
