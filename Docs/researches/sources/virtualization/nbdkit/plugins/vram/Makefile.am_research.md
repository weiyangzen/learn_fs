# File Research: sources/virtualization/nbdkit/plugins/vram/Makefile.am

Builds the OpenCL video-RAM-backed plugin when OpenCL support is available.

Key behavior:
- Distributes `nbdkit-vram-plugin.pod`.
- Guards build with `HAVE_OPENCL`.
- Builds `nbdkit-vram-plugin.la` from `opencl-errors.h`, `vram.c`, and plugin header.
- Adds common include paths and local include path.
- Uses `$(OPENCL_CFLAGS)` and links `$(OPENCL_LIBS)`.
- Links common utils and Windows import support.
- Adds plugin linker script when enabled.
- Generates `nbdkit-vram-plugin.1` from POD with magic-parameter insertion when POD support is present.

Dependencies:
- OpenCL headers/libraries.
- nbdkit common utils.
