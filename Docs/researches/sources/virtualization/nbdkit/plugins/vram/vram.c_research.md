# File Research: sources/virtualization/nbdkit/plugins/vram/vram.c

Implements the `vram` nbdkit plugin, exposing OpenCL device memory as a sparse volatile block device.

Key behavior:
- Uses OpenCL 2.0 target APIs.
- Config accepts `size=<SIZE>` and `device=<N|NAME>`.
- Enumerates all OpenCL platforms/devices into a flat list, collecting name, vendor, availability, memory size, max allocation size, and queue-on-device sizes.
- `.dump_plugin` prints detected OpenCL device inventory.
- `.config_complete` requires at least one OpenCL device, selects by index or exact name, verifies 64 KiB buffer support, defaults size to device global memory if omitted, rejects size greater than global memory, and rounds size up to 64 KiB.
- `.get_ready` stores the current pid. `.after_fork` rejects running after fork and instructs use of `nbdkit -f`, because tested OpenCL implementations can hang after fork.
- `.after_fork` initializes a sparse `buffer_map`, creates an OpenCL context for the selected platform/device, and creates a command queue.
- The disk is divided into fixed `BUFFER_SIZE` 64 KiB chunks. Each map entry either has a `cl_mem` buffer or is sparse/zero.
- `.open` returns `NBDKIT_HANDLE_NOT_NEEDED`; storage is global and shared.
- Thread model is `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`; comments note parallelism would need buffer locking.
- `.block_size` advertises 4096 minimum and 64 KiB preferred.
- `.can_multi_conn` returns true because all connections see the same global storage.
- `.pread` handles unaligned head/body/tail through a bounce buffer, reading whole 64 KiB OpenCL buffers or zero-filling sparse regions.
- `.pwrite` handles unaligned writes by read-modify-write bounce buffers; full chunks allocate OpenCL buffers on demand and write them with blocking `clEnqueueWriteBuffer`.
- `.flush` is a no-op because GPU memory is volatile.
- `.zero` keeps buffers allocated, using read-modify-write for unaligned portions and `clEnqueueFillBuffer` plus `clFinish` for aligned full buffers.
- `.trim` releases fully covered OpenCL buffers to make them sparse/zero again; partial head/tail regions are ignored.
- `.extents` reports allocated buffers as data and unallocated buffers as `HOLE|ZERO`.
- `.unload` frees device metadata and releases command queue/context.

Dependencies:
- OpenCL runtime.
- nbdkit API v2.
- vector, alignment, rounding, and ASCII helpers.

Notes and risks:
- OpenCL memory objects in `buffer_map` are not released in `.unload` unless trimmed first; only queue/context are released.
- `clCreateContextFromType` uses `CL_DEVICE_TYPE_DEFAULT` with the selected platform, while the command queue uses the selected device id; unusual platforms may mismatch if selected device is not default.
- Size is rounded up, so exported size can exceed requested size by less than 64 KiB.
- Trim only frees full buffers and does not zero partial ranges.
