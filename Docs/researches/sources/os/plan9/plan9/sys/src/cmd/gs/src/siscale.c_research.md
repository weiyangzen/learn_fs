# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.c

Smoothed image scaling stream filter based on a Mitchell filter and Graphics Gems III scaling code.

Key behavior:
- Supports fixed-point accumulation when `USE_FPU <= 0`, otherwise floating-point accumulation.
- Defines `stream_IScale_state` with source/destination row buffers, intermediate horizontally scaled rows, contribution lists, filter weights, and row offsets.
- `Mitchell_filter` supplies the reconstruction filter with support 2.0.
- `calculate_contrib` precomputes source pixel contributors and weights for a scaling dimension, including downscale widening and edge reflection/clamping.
- `zoom_x` applies horizontal filtering into a temporary row ring.
- `zoom_y` applies vertical filtering from temporary rows into destination output.
- `s_IScale_init` computes scale factors, row sizes, allocates working buffers, precomputes X contributions, and prepares the first Y contribution list.
- `s_IScale_process` streams input rows, horizontally scales each row, and emits output rows once enough temporary rows are available.
- `s_IScale_release` frees all working storage.

Notable dependencies:
- Math and config wrappers: `math_.h`, `gconfigv.h`.
- Shared parameters from `siscale.h`/`sisparam.h`.

Research notes:
- The scaler supports both encode/decode templates identically via `s_IScale_template`.
- Allocation failure is marked with the historical “WRONG” comment because it returns `ERRC` rather than VM-specific errors.
- The temporary ring is bounded by `MAX_ISCALE_SUPPORT`, limiting memory and filter support.
