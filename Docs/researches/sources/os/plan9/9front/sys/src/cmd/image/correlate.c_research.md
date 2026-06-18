# File Research: sources/os/plan9/9front/sys/src/cmd/image/correlate.c

Applies an image correlation or convolution kernel to an image read from stdin.

Key points:
- Usage: `correlate [-cRp] kernel [denom]`.
- Reads kernel files from the given path or `/lib/image/filter/<basename>`.
- `readimagekernel` parses whitespace-separated doubles into a rectangular kernel, verifies consistent row width, optionally reverses kernel coefficients for convolution mode, and calls `allocmemimagekernel`.
- Options:
  - `-c` reverses the kernel for convolution.
  - `-R` enables replicated source sampling.
  - `-p` processes row bands in parallel.
- Allocates transparent destination image and calls `memimagecorrelate`.
- Parallel mode uses `NPROC`, row rectangles from `initworkrects`, and `rfork(RFPROC|RFMEM)` workers.

Dependencies and interactions:
- Uses utility functions from `image/util.c`.
- Uses Plan 9 `memdraw` kernel/correlation APIs.

Research relevance:
- A command-line wrapper for Plan 9 image filtering kernels, with optional parallel execution.
