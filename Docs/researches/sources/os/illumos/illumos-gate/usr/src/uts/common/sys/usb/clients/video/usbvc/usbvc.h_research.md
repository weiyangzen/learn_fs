# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc.h

USB Video Class descriptor and request definitions. It defines video class/subclass/protocol constants, class-specific descriptor types/subtypes, endpoint types, request codes, control selectors, terminal types, descriptor structures, probe/commit structure, format GUIDs, and stream payload flags.

The descriptor models cover video-control headers, units, terminals, streaming input/output headers, frames, still image frame patterns, color matching, MJPEG/uncompressed formats, and video streaming probe/commit controls.

The header uses raw byte arrays for many little-endian multi-byte UVC fields, leaving conversion to implementation helpers. It defines YUY2 and NV12 format GUID initializers and stream EOF/FID bit flags.
