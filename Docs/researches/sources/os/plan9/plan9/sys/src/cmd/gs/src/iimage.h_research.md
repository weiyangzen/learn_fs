# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iimage.h

Declares image operator entry points and auxiliary image parameters.

Key points:
- Defines `image_params` for interpreter-side parameters not in core image structs: `MultipleDataSources`, `DataSource[]`, and `pDecode`.
- Declares `data_image_params`, `pixel_image_params`, `zimage_setup`, and `image1_setup`.
- Supports data and pixel image parameter extraction, including source requirements, component count, max bits per component, and alpha handling.
- Exported by `zimage.c` for image-related modules.

Research relevance:
- Interpreter-side parsing/setup interface for PostScript image operators.
