# sources/test-tools/strace/src/kernel_v4l2_types.h

Purpose: defines stable V4L2 kernel buffer/event layouts and ioctl numbers independent of libc/kernel header time type drift.

Important APIs/types/functions: `kernel_v4l2_timeval_t`, `kernel_v4l2_buffer_t`, `kernel_v4l2_buffer_time32_t`, `kernel_v4l2_event_t`, `KERNEL_V4L2_HAVE_TIME32`, redefined `VIDIOC_QUERYBUF`, `VIDIOC_QBUF`, `VIDIOC_DQBUF`, `VIDIOC_PREPARE_BUF`, time32 variants, and `VIDIOC_DQEVENT`.

Control flow: includes Linux V4L2 UAPI and kernel time headers, defines sparc64-specific timeval layout, defines normal and optional time32 buffer structs, restores removed constants, and undefines/redefines ioctl request numbers using the controlled kernel layouts.

State and persistence behavior: no runtime state; it controls compile-time structure and ioctl encodings.

Dependencies and integration points: used by V4L2 ioctl decoders so request numbers and decoded buffers match tracee kernel ABI rather than host libc `struct timeval`/`timespec`.

Risks: V4L2 structs contain unions and pointer-like members, so time32/64 and sparc64 differences can alter ioctl numbers. Removed constants are retained for decoding older traces.

Test signals: cover V4L2 buffer ioctls on time32 and time64 ABIs, event dequeue, request-fd union field, sparc64 timeval layout, and constants removed from newer kernel headers.
