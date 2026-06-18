# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/cam.c

USB Video Class camera filesystem front-end.

Key elements:
- Parses UVC video control and video streaming class descriptors from USB descriptors.
- Builds `Cam` objects for video streaming input headers, with indexed uncompressed formats and frames.
- Tracks video-control units by unit ID for use by control logic in companion files.
- Creates one directory per camera stream: `cam<hname>.<ifaceid>`.
- Exposes `ctl`, `formats`, `video`, `frame`, and `desc` files for each stream.
- `formats` reports width, height, bits-per-pixel, fourcc-like format, and frame rates/interval ranges.
- `desc` dumps UVC descriptors and current probe control.
- `ctl` is read/write through external `ctlread`/`ctlwrite`.
- `video` and `frame` use external `videoopen`, `videoread`, `videoflush`, and `videoclose`.
- Posts a USB share service named `<devid>.cam`.

Notable behavior:
- On startup, default frame index and default frame interval are copied into the probe control when available.
- Read state for string files is stored per fid and refreshed on offset zero.
- Opening `frame` passes a flag to `videoopen` to select frame-oriented behavior.

Risks and quirks:
- Error message `"the front fell off"` is used for invalid fid/file state.
- Realloc size bookkeeping uses descriptor indexes directly, leaving sparse arrays for missing indexes.
- Relies on companion UVC files (`uvc.h`, `dat.h`, `fns.h` implementations) for controls and streaming.
