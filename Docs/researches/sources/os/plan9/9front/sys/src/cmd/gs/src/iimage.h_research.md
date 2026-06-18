# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage.h

Declares image operator entry points and auxiliary image parameters.

Key points:
- Defines `image_params` for interpreter-side parameters not in core image structs:
  - `MultipleDataSources`
  - `DataSource[]`
  - `pDecode`
- Declares:
  - `data_image_params`
  - `pixel_image_params`
  - `zimage_setup`
  - `image1_setup`
- Supports data and pixel image parameter extraction, including alpha and component-count constraints.

Dependencies and interactions:
- Exported by `zimage.c`.
- Used by `zimage3.c`, `ztrans.c`, and `zdpnext.c`.

Research relevance:
- Interpreter-side parsing/setup interface for PostScript image operators.
