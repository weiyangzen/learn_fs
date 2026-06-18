# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/uvc.h

This header defines the UVC descriptor layouts, request codes, class/subclass constants, descriptor subtype constants, terminal/unit control selector constants, and little-endian helper macros used by the USB camera driver.

The descriptor structs model the variable-length UVC descriptors as C layouts with trailing one-element arrays where necessary. It includes VideoControl descriptors (`VCHeader`, terminals, selector/processing/encoding/extension units), VideoStreaming descriptors (`VSInputHeader`, `VSOutputHeader`, `VSStillFrame`, uncompressed format/frame descriptors, color format), and `ProbeControl`. These definitions are used directly by parser, control, descriptor printing, and streaming code by casting raw descriptor bytes from the USB library.

The enum section captures UVC class values (`CC_VIDEO`, `SC_VIDEOCONTROL`, `SC_VIDEOSTREAMING`), class-specific descriptor types, VideoControl and VideoStreaming subtypes, request codes (`GET_CUR`, `GET_MIN`, `GET_MAX`, `GET_RES`, `GET_INFO`, `SET_CUR`, and aggregate variants), camera-terminal controls, processing-unit controls, encoding-unit controls, streaming controls, and terminal type values such as `ITT_CAMERA`.

The header uses `GET3` in addition to the USB library's `GET2` and `GET4`. All multi-byte fields in the structs are byte arrays, which keeps descriptor interpretation endian-explicit and matches the rest of the nusb code style.
