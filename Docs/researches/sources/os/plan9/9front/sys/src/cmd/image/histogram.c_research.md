# File Research: sources/os/plan9/9front/sys/src/cmd/image/histogram.c

Implements an interactive image viewer with separate per-channel histogram windows.

Key points:
- Reads an image from stdin or a file into `Memimage`, converts it to a display `Image`, and opens a draw window.
- Maintains affine transform matrix/warp for pan and zoom of the displayed source image.
- Samples pixels manually from `Memimage` across depths 1/2/4/8/16/24/32 and channel descriptors, converting to RGBA-like values.
- `measureimage` computes alpha/blue/green/red histograms, averages, and maximum bins over the full image or selected region.
- Draws histogram images with colored bars, average marker line, and grayscale gradients.
- Starts a second window labeled `histograms` to display four stacked histogram panels.
- Mouse behavior:
  - left drag pans source image.
  - middle drag or scroll zooms.
  - right menu toggles smoothing or selects/clears a region.
  - right-drag in histogram window draws freehand marks.
- Keyboard `q` or Delete exits.
- Handles resize and keeps histogram window sized/moved via `/dev/wctl`.

Dependencies and interactions:
- Uses Plan 9 `thread`, `draw`, `memdraw`, `mouse`, `keyboard`, and `geometry`.
- Uses `image/util.c` helpers for allocation and image conversion.

Research relevance:
- A richer interactive image-analysis tool demonstrating Plan 9 graphics, windows, channels, event loops, and raw pixel interpretation.
