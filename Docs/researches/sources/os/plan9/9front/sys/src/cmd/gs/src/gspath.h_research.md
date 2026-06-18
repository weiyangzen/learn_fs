# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.h

Declares graphics-state path APIs.

Exports:
- Path constructors for move/line/curve/arc/closepath.
- Imager-level arc helpers.
- Path transformers/accessors: `gs_currentpoint`, `gs_upathbbox`, `gs_dashpath`, `gs_flattenpath`, `gs_reversepath`, `gs_strokepath`.
- Path enumeration allocation, initialization, iteration, and cleanup.
- Clipping operations: `gs_clippath`, `gs_initclip`, `gs_clip`, `gs_eoclip`.

Also defines `gs_pathbbox` as a wrapper around `gs_upathbbox(..., false)`.
