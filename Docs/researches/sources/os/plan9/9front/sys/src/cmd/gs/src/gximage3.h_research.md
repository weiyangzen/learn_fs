# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.h

Internal API for Ghostscript ImageType 3 processing.

Key contents:
- Defines callback signatures for creating the mask image device and the mask clipping device/enumerator.
- Documents that the ImageType 3 splitter is used both for rendering and high-level output writers.
- Exports `gx_begin_image3_generic`, parameterized by the mask-device and mask-clip setup callbacks.

Notable dependencies:
- `gsiparm3.h` for ImageType 3 public parameters.
- `gxiparam.h` for typed image and enumerator interfaces.

Research notes:
- This is a small virtualized setup layer that lets output devices reuse mask/pixel splitting without necessarily using the default memory-mask clipping device.
