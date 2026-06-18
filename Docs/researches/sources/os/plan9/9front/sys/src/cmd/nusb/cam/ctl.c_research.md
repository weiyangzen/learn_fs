# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/ctl.c

This file implements the control-plane surface for the 9front USB Video Class camera driver. It defines a `Param` table mapping user-visible control names to UVC control selectors, value lengths, advertised-control bitmap bits, and per-type read/write handlers. The file is responsible for turning textual 9P `ctl` messages into UVC `GET_*` and `SET_CUR` control transfers, and for formatting available camera state back into readable lines.

The low-level helpers cover booleans, signed integers, unsigned integers, and enumerated values. Reads first use `GET_INFO` through `infocheck()` to verify that a control supports `GET`, then issue `GET_CUR`, and for numeric values also `GET_MIN`, `GET_RES`, and `GET_MAX`. Failed control requests call `errorcode()`, which fetches `VC_REQUEST_ERROR_CODE_CONTROL` from the relevant terminal/unit and maps UVC error codes to Plan 9 error strings.

Special parameters handle stream format and frame rate. `pformatread()` reports the current probe-control format/frame as `<width>x<height>x<bits>-<fourcc>`, falling back to numeric format/frame indices if descriptors are missing. `pformatwrite()` parses `WIDTHxHEIGHT` or `WIDTHxHEIGHTxBPP-FOURCC`, searches the parsed format/frame descriptor arrays, refuses changes while the camera is active, and snaps the frame interval to a valid interval for the selected frame. `pfpsread()` and `pfpswrite()` expose `dwFrameInterval` as frames per second, again rejecting changes while active.

`ctlread()` enumerates all special controls plus camera-terminal and processing-unit controls actually advertised by descriptor bitmaps. `ctlwrite()` accepts either an explicit unit id followed by parameter name, or an automatic form where the parameter name selects the first matching unit type. It validates unit type, advertised support, and write availability before dispatching to the parameter writer.

Key dependencies are the global UVC descriptor arrays `unit`, `unitif`, and `nunit` declared in `dat.h`, `ProbeControl` and selector constants from `uvc.h`, and `getframedesc()` from `video.c`.
