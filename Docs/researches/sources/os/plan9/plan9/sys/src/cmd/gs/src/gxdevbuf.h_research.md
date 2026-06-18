# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevbuf.h

Defines buffer-device management procedure vectors.

- Associated mainly with printer and banded devices, though comments leave room for wider use.
- Includes `gxrplane.h` for render-plane structures.
- Defines `gx_device_buf_space_t`:
  - `bits`
  - `line_ptrs`
  - `raster`
- Defines `gx_device_buf_procs_t` with methods:
  - `create_buf_device`
  - `size_buf_device`
  - `setup_buf_device`
  - `destroy_buf_device`
- `create_buf_device` may allocate or initialize an existing memory device depending on whether `mem` is NULL.
- `setup_buf_device` supports both full-band buffers and partial-band scanline readout buffers.
- Declares default implementations:
  - `gx_default_create_buf_device`
  - `gx_default_size_buf_device`
  - `gx_default_setup_buf_device`
  - `gx_default_destroy_buf_device`

Concurrency note: for async devices, `size_buf_device` may be called by writer or reader threads; other procedures are reader-thread-only.
