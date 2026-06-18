# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/videodev2.h

## Role

`videodev2.h` is an illumos copy/adaptation of the public Video4Linux2 userspace ABI. It defines video-device capabilities, pixel formats, buffer formats, controls, tuners, audio, VBI data structures, and `VIDIOC_*` ioctl numbers.

## Key Interfaces

The header defines:
- legacy V4L1-style `VID_TYPE_*` capability bits.
- `v4l2_fourcc()` and many `V4L2_PIX_FMT_*` FourCC pixel formats.
- enums for fields, buffer types, control types, tuner types, memory models, colorspaces, and priority.
- base geometry types `v4l2_rect` and `v4l2_fract`.
- `struct v4l2_capability` and `V4L2_CAP_*` feature bits.
- `struct v4l2_pix_format`, `v4l2_fmtdesc`, `v4l2_timecode`, JPEG compression settings, request buffers, stream buffers, framebuffer/overlay structures, capture/output parameters, crop structures, standards, inputs, outputs, controls, tuners, modulators, frequencies, audio endpoints, raw VBI, sliced VBI, aggregate `v4l2_format`, and `v4l2_streamparm`.

## ABI and Alignment Notes

The file includes illumos-specific compatibility changes:
- It uses `<sys/ioccom.h>` ioctl encoding.
- It defines `struct v4l2_timeval` using fixed-width `uint64_t` fields instead of native `long`-based `timeval`.
- It uses `#pragma pack(4)` for selected structures when 64-bit kernel alignment differs from 32-bit alignment.
- It adds explicit padding in `v4l2_input` and `v4l2_format` to keep 32-bit applications and 64-bit drivers in agreement.

## Ioctls

The ioctl list covers capability query, format enumeration/get/set/try, buffer request/query/queue/dequeue, streaming on/off, framebuffer, overlay, parameters, video standards, inputs/outputs, controls, tuners, audio, modulators, frequencies, crop, JPEG compression, priority, sliced VBI capability, status logging, and extended controls.

Private ioctl numbers start at `BASE_VIDIOC_PRIVATE = 192`.

## Research Notes

This header is ABI-heavy. Changes to structure layout, packing, enum values, or ioctl numbers can break binary compatibility with applications and drivers. Some old MPEG compression definitions are guarded by `__KERNEL__` and marked obsolete in comments.
