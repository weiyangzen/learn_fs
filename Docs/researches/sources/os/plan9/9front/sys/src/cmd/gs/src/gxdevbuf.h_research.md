# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevbuf.h

This header defines the buffer-device management procedure table used by printer and banded devices. It includes `gxrplane.h` for render-plane descriptions and forward-declares `gx_device`.

`gx_device_buf_space_t` reports buffer requirements as bit storage size, line pointer storage size, and raster. `gx_device_buf_procs_t` contains four callbacks: `create_buf_device`, `size_buf_device`, `setup_buf_device`, and `destroy_buf_device`.

The callbacks cover creating memory/buffer devices for a page or band, computing required storage, attaching a specific buffer and optional line-pointer area, and destroying the buffer device without freeing the buffered pixel data. The comments note async-device threading constraints: `size_buf_device` may be called by writer or reader, while the other callbacks are reader-thread-only.

The header declares default implementations for all four callbacks.

Filesystem relevance: indirect only. It deals with page/band render buffers in memory, not filesystem buffers or storage block caches.
