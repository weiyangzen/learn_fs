# File Research: sources/os/bsd/openbsd-src/sys/sys/videoio.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-6358, source bytes 262131, report `Docs/researches/chunks/chunk_sources_os_bsd_openbsd_src_sys_sys_videoio_h_1_1_6358_a715135f0b62_research.md`
- chunk 2: lines 6359-6403, source bytes 2126, report `Docs/researches/chunks/chunk_sources_os_bsd_openbsd_src_sys_sys_videoio_h_2_6359_6403_a2f70d6088b3_research.md`

## Chunk Research

### Chunk 1: lines 1-6358

# Chunk Research: sources/os/bsd/openbsd-src/sys/sys/videoio.h lines 1-6358

## Scope

This chunk covers lines 1-6358 of OpenBSD's `sys/sys/videoio.h`, a public V4L2-compatible video device ABI header. The full file has 6403 lines; this chunk includes the license/header guard, inlined Linux V4L2 common/control definitions, most public V4L2 data structures, format IDs, state/control flags, helper macros, the single inline timestamp helper, and ioctl command definitions through `VIDIOC_TRY_ENCODER_CMD`. Lines after 6358 continue the ioctl list and close the header.

## Purpose and API Surface

The header exposes a user/kernel ABI for video, radio, SDR, touch, metadata, codec, and media-control style devices. It is declaration-heavy: it defines constants, enums, structure layouts, unions, packed ABI payloads, and ioctl request numbers rather than implementing driver logic.

Major exported areas in this chunk:

- Selection and EDID API: `V4L2_SEL_TGT_*`, `V4L2_SEL_FLAG_*`, compatibility aliases, and `struct v4l2_edid`.
- Control classes and IDs: user, codec, camera, FM TX/RX, flash, JPEG, image source/processing, DV, RF tuner, detection, stateless codec, and colorimetry control namespaces.
- Codec control payloads: stateful MPEG/H.26x/VPx/HEVC/AV1 controls and stateless decode parameter structs for H.264, FWHT, VP8, MPEG-2, HEVC, VP9, and AV1.
- Core V4L2 stream model: buffer types, memory types, fields, colorspace/transfer/YCbCr/HSV/quantization enums, capability flags, pixel format structures, buffer queue structures, and stream parameter structures.
- Format identifiers: a large catalog of `v4l2_fourcc()` and `v4l2_fourcc_be()` pixel/data format constants for RGB, greyscale, YUV, Bayer, tiled, compressed codec streams, vendor formats, SDR, touch, and metadata payloads.
- Device discovery and configuration structs: capability, format enumeration, frame size/interval enumeration, standards, DV timings/caps, input/output descriptors, tuning/modulator/frequency structs, audio/audioout structs, VBI and sliced VBI structs.
- Event/debug/buffer-management structs: event payloads/subscription, debug chip/register payloads, create/remove buffer payloads.
- Ioctl request definitions through line 6358: query capability, enum/get/set/try format, buffer queueing, streaming, standards, controls, tuner/audio, EDID, crop/selection, extended controls, frame size/intervals, encoder commands, and the start of the advanced-debug ioctl section.

## Dependencies and ABI Assumptions

The header includes OpenBSD system headers `sys/time.h`, `sys/types.h`, and `sys/ioccom.h`. It depends on OpenBSD integer typedefs such as `u_int8_t`, `u_int16_t`, `u_int32_t`, and `u_int64_t`, `struct timeval`, `struct timespec`, ioctl encoding macros `_IO`, `_IOR`, `_IOW`, `_IOWR`, and compiler support for `__attribute__((packed))`.

The file inlines material from Linux `v4l2-common.h` and `v4l2-controls.h`, but adapts it to OpenBSD-style public headers. `__user` is defined empty when not already present, so user-pointer annotations remain syntactically available without requiring Linux headers. Several payload structs use raw user pointers, for example `struct v4l2_ext_control`, `struct v4l2_buffer`, `struct v4l2_clip`, and `struct v4l2_window`; kernel ioctl handlers must validate/copy those addresses.

Macros such as `_BITUL()` and `GENMASK()` are referenced in the FWHT flag block. They are not defined in this chunk, so consumers must receive them from other OpenBSD headers or from earlier compatibility definitions in the effective include graph. This is a visible dependency risk if the header is compiled standalone outside its intended environment.

## Control Flow and State

There is almost no executable control flow. The only function body in this chunk is:

- `static inline u_int64_t v4l2_timeval_to_ns(const struct timeval *tv)`, which converts seconds and microseconds to nanoseconds.

All other behavior is encoded as ABI state machines and ioctl payload contracts:

- Buffer lifecycle state is represented by `struct v4l2_requestbuffers`, `struct v4l2_buffer`, `struct v4l2_plane`, `struct v4l2_exportbuffer`, `struct v4l2_create_buffers`, and `struct v4l2_remove_buffers`, plus flags such as `V4L2_BUF_FLAG_MAPPED`, `QUEUED`, `DONE`, `ERROR`, `IN_REQUEST`, `PREPARED`, `LAST`, and timestamp/source masks.
- Streaming control is exposed by `VIDIOC_REQBUFS`, `QUERYBUF`, `QBUF`, `DQBUF`, `EXPBUF`, `STREAMON`, `STREAMOFF`, `PREPARE_BUF`, and `CREATE_BUFS`; actual queue transitions are implemented by drivers, not this header.
- Control state is represented by scalar `struct v4l2_control`, compound `struct v4l2_ext_control`, batches in `struct v4l2_ext_controls`, query descriptors, control IDs, control types, and flags like disabled/read-only/write-only/volatile/dynamic-array.
- Codec decode state is represented in userspace-supplied parameter structs: H.264 SPS/PPS/scaling/prediction/slice/decode params, DPB entries, HEVC SPS/PPS/slice/decode/RPS params, VP8/VP9 segmentation/filter/probability structs, MPEG-2 sequence/picture/quantisation structs, FWHT params, AV1 sequence/tile/frame/film grain structs.
- Device signal/input/output state is represented by standards bitmasks, input/output status/capability bits, tuner/modulator frequency ranges, RDS blocks, DV timing capabilities, events, and debug register payloads.

## Data Model Highlights

The ABI is heavily union-based. `struct v4l2_format` dispatches on `type` to image, multi-plane image, overlay window, VBI, sliced VBI, SDR, metadata, or raw data layouts. `struct v4l2_streamparm` dispatches capture vs output timing parameters. `struct v4l2_ext_control` dispatches scalar, string, raw pointer, and many codec/control-specific payload pointers.

Several structures are explicitly packed to preserve Linux-compatible layouts across compilers and platforms, including many codec/control/query/VBI/timing payloads. Reserved arrays are common and comments repeatedly require applications and drivers to zero them; this is central to forward compatibility.

Pixel and metadata formats are represented by FourCC constants. This chunk defines the helper macros `v4l2_fourcc()` and `v4l2_fourcc_be()` and then enumerates many formats. The big-endian helper sets bit 31, so code comparing or serializing FourCC values must preserve that flag.

Colorimetry defaults are specified by mapping macros:

- `V4L2_MAP_COLORSPACE_DEFAULT`
- `V4L2_MAP_XFER_FUNC_DEFAULT`
- `V4L2_MAP_YCBCR_ENC_DEFAULT`
- `V4L2_MAP_QUANTIZATION_DEFAULT`

These macros are simple nested conditional expressions and do not validate enum values.

## Risks and Edge Cases

- ABI layout risk: this is a public ioctl ABI header. Changes to field sizes, ordering, packing, or enum/control IDs can break existing userland or driver compatibility.
- Pointer-width risk: structures contain `unsigned long` and pointers in ioctl payload unions. Compatibility layers for 32-bit userland on 64-bit kernels must translate them carefully; a comment after this chunk's boundary explicitly reminds maintainers to update Linux compat ioctl handling when adding ioctls.
- User pointer risk: `__user` is empty here, so static analysis cannot rely on the annotation in OpenBSD builds. Kernel code must still treat all user pointers as untrusted.
- Reserved-field risk: many structs require reserved fields to be zero. Drivers should reject or ignore nonzero reserved bits consistently to avoid ABI ambiguity and future-extension conflicts.
- Bitmask collision risk: aliases and deprecated definitions are intentionally retained, for example MPEG-to-codec control aliases, old selection aliases, tuner language/SAP aliases, deprecated colorspace names, and later compatibility capabilities. Consumers should avoid interpreting aliases as independent capabilities.
- Macro dependency risk: `_BITUL()` and `GENMASK()` appear in this header region but are not defined in this chunk. If not supplied by included headers, FWHT flag definitions will not compile.
- Range/array risk: stateless codec structs contain large fixed arrays and dynamic-array control comments. Drivers must validate `size`, `count`, dimensions, and control type before trusting user payloads.
- Time conversion risk: `v4l2_timeval_to_ns()` performs unchecked arithmetic; extreme `tv_sec` values can overflow `u_int64_t`, though normal V4L2 timestamps should not approach that range.

## Cross-Chunk References

This is chunk 1 and ends at line 6358 after `VIDIOC_TRY_ENCODER_CMD` and before the remaining ioctl definitions. The next chunk or merge step must account for the continuation of the ioctl block: debug register ioctls, hardware frequency seek, DV timing/event subscription/ioctl definitions, create/prepare/selection/decoder/frequency-band/chip-info/query-ext/remove-buffer ioctls, `BASE_VIDIOC_PRIVATE`, deprecated compatibility aliases, `V4L2_CAP_ASYNCIO`, and the closing header guard.

Within this chunk, comments reference external implementation files and Linux/OpenBSD driver layers not present here, including V4L2 core ioctl compatibility handling, codec specifications, device-tree SDTV standard bindings, media controller/subdevice conventions, and driver-specific control namespaces. Those are integration references rather than local definitions.

## Research Notes

Read scope: complete line range 1-6358. This report is intentionally a chunk report only and does not create or replace the merged per-file report at `Docs/researches/sources/os/bsd/openbsd-src/sys/sys/videoio.h_research.md`.

### Chunk 2: lines 6359-6403

# Chunk Research: sources/os/bsd/openbsd-src/sys/sys/videoio.h lines 6359-6403

## Scope

This chunk covers the final 45 lines of OpenBSD's `sys/sys/videoio.h`. It completes the public V4L2-compatible ioctl request-number block, reserves the private ioctl range, keeps two deprecated pixel-format aliases for source compatibility, defines a deprecated/unimplemented capability bit, and closes the `_SYS_VIDEOIO_H_` header guard.

The chunk is declaration-only. It does not implement driver behavior, but it is ABI-significant because these macros encode ioctl command numbers, direction bits, and payload structure types.

## APIs and ABI Surface

The exported ioctl macros in this chunk all use OpenBSD ioctl encoding macros from `sys/ioccom.h` with ioctl group `'V'`:

- Advanced debug register access: `VIDIOC_DBG_S_REGISTER` uses `_IOW('V', 79, struct v4l2_dbg_register)`, while `VIDIOC_DBG_G_REGISTER` uses `_IOWR('V', 80, struct v4l2_dbg_register)`. The preceding comment from lines 6354-6358 says these are experimental, require advanced-debug support, require root, and should not be used by applications.
- Hardware frequency seek: `VIDIOC_S_HW_FREQ_SEEK` writes `struct v4l2_hw_freq_seek`.
- Digital video timings: `VIDIOC_S_DV_TIMINGS`, `VIDIOC_G_DV_TIMINGS`, `VIDIOC_ENUM_DV_TIMINGS`, `VIDIOC_QUERY_DV_TIMINGS`, and `VIDIOC_DV_TIMINGS_CAP` expose timing set/get/enumeration/query/capability operations over `struct v4l2_dv_timings`, `struct v4l2_enum_dv_timings`, and `struct v4l2_dv_timings_cap`.
- Event queue API: `VIDIOC_DQEVENT`, `VIDIOC_SUBSCRIBE_EVENT`, and `VIDIOC_UNSUBSCRIBE_EVENT` use `struct v4l2_event` and `struct v4l2_event_subscription`.
- Buffer lifecycle extensions: `VIDIOC_CREATE_BUFS`, `VIDIOC_PREPARE_BUF`, and `VIDIOC_REMOVE_BUFS` use `struct v4l2_create_buffers`, `struct v4l2_buffer`, and `struct v4l2_remove_buffers`.
- Selection/cropping replacement API: `VIDIOC_G_SELECTION` and `VIDIOC_S_SELECTION` use `struct v4l2_selection`.
- Decoder command API: `VIDIOC_DECODER_CMD` and `VIDIOC_TRY_DECODER_CMD` use `struct v4l2_decoder_cmd`.
- Frequency band enumeration: `VIDIOC_ENUM_FREQ_BANDS` uses `struct v4l2_frequency_band`.
- Debug chip discovery: `VIDIOC_DBG_G_CHIP_INFO` uses `struct v4l2_dbg_chip_info`; its local comment again marks it experimental/debug/internal only.
- Extended control query: `VIDIOC_QUERY_EXT_CTRL` uses `struct v4l2_query_ext_ctrl`.

The chunk also exports `BASE_VIDIOC_PRIVATE` as `192`, documenting that ioctl numbers `192-255` are private. Two deprecated names remain as aliases: `V4L2_PIX_FMT_HM12` maps to `V4L2_PIX_FMT_NV12_16L16`, and `V4L2_PIX_FMT_SUNXI_TILED_NV12` maps to `V4L2_PIX_FMT_NV12_32L32`. `V4L2_CAP_ASYNCIO` is kept at bit value `0x02000000`, but the comment says this capability was never implemented and users should remove it.

## Control Flow and State

There is no executable control flow in this chunk. The visible behavior is encoded as ioctl ABI contracts:

- `_IOW` commands represent userland-to-kernel input payloads: setting debug registers, seeking hardware frequency, subscribing/unsubscribing events.
- `_IOR` commands represent kernel-to-user output payloads: dequeuing an event and querying current DV timings.
- `_IOWR` commands represent bidirectional payloads where callers provide selectors, indexes, or requested parameters and drivers return negotiated or current state.

The state surfaces named by this chunk are all owned by V4L2 drivers or the V4L2 core rather than this header: debug register state, tuner seek state, DV timing state, event subscriptions and event queue contents, buffer allocation/preparation/removal state, selection rectangles, decoder command state, frequency band inventory, debug chip metadata, and extended-control metadata.

## Dependencies

These macros depend on definitions earlier in the same header and on included system headers:

- `_IO`, `_IOR`, `_IOW`, and `_IOWR` come from `sys/ioccom.h`.
- Payload structs are defined before this chunk: `struct v4l2_dbg_register`, `struct v4l2_hw_freq_seek`, `struct v4l2_dv_timings`, `struct v4l2_event`, `struct v4l2_event_subscription`, `struct v4l2_create_buffers`, `struct v4l2_buffer`, `struct v4l2_selection`, `struct v4l2_decoder_cmd`, `struct v4l2_enum_dv_timings`, `struct v4l2_dv_timings_cap`, `struct v4l2_frequency_band`, `struct v4l2_dbg_chip_info`, `struct v4l2_query_ext_ctrl`, and `struct v4l2_remove_buffers`.
- Alias targets `V4L2_PIX_FMT_NV12_16L16` and `V4L2_PIX_FMT_NV12_32L32` are defined earlier as tiled NV12 FourCC values.
- The comment at lines 6389-6390 references Linux's `drivers/media/v4l2-core/v4l2-compat-ioctl32.c`; this OpenBSD header preserves that imported-maintenance warning even though the file is not local to this header.

## Risks and Edge Cases

- ABI stability risk: ioctl numbers, directions, and payload structure types are public ABI. Renumbering or changing `_IOR`/`_IOW`/`_IOWR` directionality would break userland/kernel compatibility.
- Compatibility-layer risk: the explicit reminder to update 32-bit ioctl compatibility handling is relevant because many payload structs contain pointers, `unsigned long`, unions, or layout-sensitive reserved fields. OpenBSD consumers need equivalent care even if the referenced Linux file is not present.
- Debug ioctl exposure risk: the debug register and chip-info ioctls are marked experimental/internal. Kernel handlers must enforce privilege and avoid exposing unsafe register access to normal applications.
- Private ioctl collision risk: `BASE_VIDIOC_PRIVATE` reserves `192-255` for private commands. Drivers using private numbers below 192 or colliding with public numbers would create ABI conflicts.
- Deprecated alias risk: `V4L2_PIX_FMT_HM12` and `V4L2_PIX_FMT_SUNXI_TILED_NV12` are aliases, not distinct formats. Code that treats them as separate capabilities may duplicate or misreport supported formats.
- Dead capability risk: `V4L2_CAP_ASYNCIO` has a bit value but is documented as never implemented. Applications should not use this bit as evidence that asynchronous I/O exists.

## Cross-Chunk References

This chunk continues directly from chunk 1, which defined the required payload structs, FourCC constants, capability bits, and ioctl commands through `VIDIOC_TRY_ENCODER_CMD` at line 6352. The advanced-debug comment that governs `VIDIOC_DBG_S_REGISTER` and `VIDIOC_DBG_G_REGISTER` begins in chunk 1 at lines 6354-6358 and terminates immediately before this chunk's first macro.

The final merged per-file report should connect this tail section to the earlier buffer, event, selection, DV timing, frequency, debug, and extended-control structure definitions. This chunk intentionally does not create or replace the per-file report at `Docs/researches/sources/os/bsd/openbsd-src/sys/sys/videoio.h_research.md`.

## Research Notes

Read scope: complete line range 6359-6403, with adjacent context from lines 6320-6358 used only to confirm ioctl-list continuity and the comment applying to the debug register ioctls. Scope is within `Docs/research_subset_a.md`.
