# File Research: sources/os/linux/linux/fs/fuse/virtio_fs.c

Implements the virtio-fs kernel driver and filesystem type, connecting FUSE request queues to virtio virtqueues, exposing device sysfs state, supporting optional DAX, and mounting by virtiofs tag.

Major structures:
- `struct virtio_fs`: one virtio-fs device instance, including tag, virtqueues, CPU queue map, optional DAX window, and sysfs kobjects.
- `struct virtio_fs_vq`: per-virtqueue state with lock, virtqueue pointer, pending/end queues, work items, `fuse_dev`, connected state, and in-flight accounting.
- `struct virtio_fs_forget`: high-priority `FUSE_FORGET` request wrapper.

Key areas:
- Mount parameter parsing supports `dax`, `dax=always`, `dax=never`, and `dax=inode`.
- Sysfs exposes `/sys/fs/virtiofs/<id>/tag` and queue attributes under `mqs`.
- Probe reads the virtio tag, sets up virtqueues, maps request queues to CPUs, sets up DAX if available, marks device ready, and registers the instance.
- Remove stops queues, drains work, resets device, deletes sysfs, and drops references.

Request flow:
- `virtio_fs_send_req()` assigns FUSE unique IDs, selects a request queue using `mq_map[raw_smp_processor_id()]`, and calls `virtio_fs_enqueue_req()`.
- `virtio_fs_enqueue_req()` builds scatterlists for FUSE headers, argument bounce buffer, and page folios, queues them with `virtqueue_add_sgs()`, links the request into the FUSE processing hash, sets `FR_SENT`, and kicks the device.
- Completion interrupts schedule work; `virtio_fs_requests_done_work()` collects completed buffers, verifies response length/unique, and ends requests directly or via worker if `may_block`.
- Queue-full requests are placed on `queued_reqs` and retried from dispatch work.
- `FUSE_FORGET` uses the hiprio virtqueue through `virtio_fs_send_forget()` and `send_forget_request()`.

DAX:
- `virtio_fs_setup_dax()` allocates a DAX device, discovers the virtio shared memory cache region, reserves/remaps it with `devm_memremap_pages()`, and records physical/kaddr window state.
- DAX ops implement direct access and zero-page-range over the shared cache window.

Mount/superblock lifecycle:
- `virtio_fs_get_tree()` finds the tag instance, creates FUSE connection/mount objects, caps `fc->max_pages_limit` to virtqueue size minus protocol overhead, and uses `sget_fc()`.
- `virtio_fs_fill_super()` allocates one `fuse_dev` per virtqueue, validates DAX mode, calls `fuse_fill_super_common()`, installs devices, starts queues, and sends FUSE init.
- `virtio_fs_conn_destroy()` cancels DAX work, stops forget/all queues, drains, destroys the FUSE connection, and frees fuse devices.
- `virtio_kill_sb()` handles superblock teardown.

Dependencies and integration:
- Integrates virtio core, FUSE core, sysfs/kobject, DAX, fs_context, iomap-style page folio request plumbing, and workqueues.
- Registers `virtio_driver` for `VIRTIO_ID_FS` and `file_system_type` named `virtiofs`.

Risks and invariants:
- `virtio_fs_mutex` protects instance list and remove/mount teardown races.
- In-flight counters and completions ensure removal/unmount waits for queued/completing requests.
- Response verification catches short, mismatched-length, and mismatched-unique replies.
- Suspend/freeze is explicitly unsupported and returns `-EOPNOTSUPP`.
- Interrupt requests are TODO; blocking lock interruption is not implemented.
