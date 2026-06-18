# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc_var.h

Internal USB video class driver state. It includes USBA private APIs, V4L2 types, and public UVC definitions, then layers PM, buffer management, stream-interface state, format grouping, V4L2 control mapping, and driver helper prototypes.

Important structures include `usbvc_buf_t` for raw camera buffers and mmap metadata, `usbvc_buf_grp_t` for free/done/filling lists, `usbvc_format_group_t` for format/frame/still/color plus V4L2 pixel metadata, `usbvc_stream_if_t` for streaming interface state and isochronous pipe/polling/buffer state, and `usbvc_state` for the whole device.

Macros cover copyin/copyout boilerplate, little-endian conversion, minimum descriptor lengths, high-speed packet size calculation, buffer status values, debug masks, buffer count limits, and UVC frame interval units.

Function prototypes expose isochronous pipe/polling, VC/VS controls, probe/commit negotiation, mmap buffer allocation/free, and V4L2 ioctl/color/GUID helpers.
