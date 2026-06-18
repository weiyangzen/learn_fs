# File Research: sources/os/linux/linux-stable/fs/fuse/virtio_fs.c

## Purpose
Implements the virtio-fs transport and filesystem registration layer, connecting FUSE request queues to virtqueues, exposing virtiofs instances in sysfs, handling mount-by-tag lookup, and supporting optional DAX shared memory windows.

## Key Interfaces
- Virtio driver callbacks: `virtio_fs_probe()`, `virtio_fs_remove()`, and suspend stubs.
- Filesystem callbacks: `virtio_fs_init_fs_context()`, `virtio_fs_get_tree()`, `virtio_fs_fill_super()`, and `virtio_kill_sb()`.
- FUSE queue ops: `virtio_fs_send_req()`, `virtio_fs_send_forget()`, `virtio_fs_send_interrupt()`, and `virtio_fs_fiq_release()`.
- Virtqueue helpers: `virtio_fs_enqueue_req()`, request/hiprio done workers, dispatch workers, and queue drain/start/stop helpers.
- DAX helpers: `virtio_fs_direct_access()`, `virtio_fs_zero_page_range()`, and `virtio_fs_setup_dax()`.

## Control Flow And Behavior
Probe reads the virtio tag, sets up one hiprio queue plus request queues, maps CPUs to request queues, optionally maps a DAX cache region, marks the device ready, and adds the instance to a global tag list and sysfs. Mount lookup finds an instance by source tag, creates a FUSE connection, constrains `max_pages_limit` to virtqueue capacity, and fills the superblock.

Normal requests are assigned unique IDs, converted into scatterlists containing headers, bounced argument buffers, and optional folios, then submitted to a CPU-selected request virtqueue. Completed requests are verified for length and unique ID, copied from the bounce buffer, zero-filled if needed, and ended. Blocking completions are moved to worker context. FORGET requests use the hiprio queue and are freed on completion.

Queue removal and unmount use `virtio_fs_mutex`, connected flags, in-flight counters, completions, and work flushing to avoid racing queue teardown with request completion.

## Dependencies
Uses virtio core, FUSE connection/device internals, FUSE DAX, sysfs/kobject APIs, fs_context parsing, scatterlists, CPU affinity helpers, devm memory remapping, and iomap/page primitives.

## Risks And Invariants
The global instance list enforces unique tags. Newlines in tags are rejected for sysfs/uevent safety. Requests must not outgrow virtqueue scatter capacity, so FUSE `max_pages_limit` is clamped. Queue teardown must stop new submissions, wait for in-flight requests, flush work, then reset/delete virtqueues. Interrupt requests are intentionally unimplemented.
