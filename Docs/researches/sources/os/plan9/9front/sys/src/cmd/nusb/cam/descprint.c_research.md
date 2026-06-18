# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/descprint.c

This file provides diagnostic pretty-printers for USB Video Class descriptors and probe-control state. Each `print*` function accepts a Plan 9 `Fmt` and a raw descriptor pointer, casts it to the relevant UVC structure from `uvc.h`, and emits a labeled multi-line textual view.

The VideoControl side covers headers, input terminals, output terminals, camera terminals, selector units, processing units, encoding units, and extension units. Camera-terminal and processing-unit printers expose important control metadata such as terminal/unit ids, terminal type, source id, focal lengths, control sizes, and `bmControls` bitmaps. Extension and selector unit printers handle variable-length source-id/control arrays by walking through trailing bytes.

The VideoStreaming side covers input/output headers, still-frame descriptors, uncompressed format descriptors, uncompressed frame descriptors, and color-format descriptors. Frame printing includes dimensions, bit-rate bounds, frame-buffer size, default interval, and either continuous min/max/step interval data or discrete frame intervals.

`printProbeControl()` dumps every field of a UVC probe/commit control block, including format/frame indices, frame interval, max frame and payload sizes, version fields, H.264-related fields, and layout-per-stream entries. `printDescriptor()` is the dispatcher: it uses the interface subclass and descriptor subtype to select the correct printer, with unknown subtype messages for unsupported VideoControl or VideoStreaming descriptors.

This file has no device I/O side effects; it is purely formatting support for camera introspection files and debug output.
