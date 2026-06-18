# File Research: sources/virtualization/qemu/hw/virtio/virtio-mem.c

Implements the virtio-mem device: guest-driven memory plug/unplug requests, block bitmap tracking, RAM discard management, dynamic memslot activation, migration state, device properties, and reset behavior.

Key entry points:
- `virtio_mem_device_realize()` validates the memory backend and properties, sets up discard management, initializes the block bitmap, virtio device, request queue, optional dynamic memslots, RAM migration registration, early migration state, and reset helper object.
- `virtio_mem_handle_request()` consumes guest requests from the virtqueue and dispatches plug, unplug, unplug-all, and state queries.
- `virtio_mem_state_change_request()` validates guest ranges, requested-size policy, current block state, and then changes block state.
- `virtio_mem_set_block_state()` performs the actual plug/unplug operation, including migration-busy checks, RAM discard/preallocation, listener notifications, bitmap updates, and dynamic memslot activation/deactivation.
- `virtio_mem_get_config()` exposes block size, NUMA node, requested size, plugged size, base address, region size, and usable region size.
- `virtio_mem_get_features()` advertises ACPI PXM, unplugged-inaccessible, and persistent-suspend features when applicable.
- RamDiscardManager methods expose plug/discard state to other QEMU subsystems.

Memory model:
- The memory backend is divided into fixed-size blocks tracked by `vmem->bitmap`; set bits are plugged, clear bits are unplugged.
- `vmem->size` is the current plugged size and `vmem->requested_size` is the target the guest may plug up to.
- `usable_region_size` can exceed requested size by an architecture-specific extent to help guests add full memory sections while only plugging part of them.
- Block size defaults are chosen from backend page size and transparent huge page expectations, with a hard minimum of 1 MiB.

Guest request behavior:
- `VIRTIO_MEM_REQ_PLUG` plugs an aligned range only if all blocks are currently unplugged and the result does not exceed requested size.
- `VIRTIO_MEM_REQ_UNPLUG` unplugs an aligned range only if all blocks are currently plugged.
- `VIRTIO_MEM_REQ_UNPLUG_ALL` discards all RAM, clears the bitmap, resets plugged size, notifies listeners, and shrinks usable region when possible.
- `VIRTIO_MEM_REQ_STATE` returns plugged, unplugged, or mixed for a valid aligned range.
- Invalid protocol buffer sizes or unknown request types call `virtio_error()`.

RAM discard and listener integration:
- Unplug uses `ram_block_discard_range()` and then notifies registered `RamDiscardListener`s of discarded sections.
- Plug can preallocate backend memory, activates dynamic memslots before notifications, notifies listeners of populated sections, and rolls back on notifier/preallocation failure.
- Registered listeners receive replay of already plugged sections; unregistering discards the listener's whole section if any memory is plugged.
- `is_populated`, `replay_populated`, and `replay_discarded` answer state by intersecting requested memory sections with the virtio-mem bitmap.

Dynamic memslots:
- With `dynamic-memslots=on`, the device creates an intermediate container memory region and per-slot aliases into the backend.
- Memslots are added only when needed for plugged memory and removed when fully unplugged.
- Memslot size is chosen before realize based on the machine limit, backend size, block size, and a minimum target of 1 GiB except for the last slot.
- Dynamic memslots require `unplugged-inaccessible=on`.

Migration:
- Early migration state can transfer immutable geometry and the bitmap before RAM migration starts.
- Sanity checks reject migration if address, backend region size, block size, or NUMA node changed.
- Post-load activates memslots for plugged ranges, replays populate notifications, discards unplugged memory, and handles preallocation before RAM migration when early migration is enabled.
- Migration-busy checks block plug/unplug while migration is running or incoming postcopy is active.
- Shared RAM ignored by QEMU migration skips discard/preallocation post-load handling.

Realize-time validation:
- Requires a memory backend that is unmapped, RAM, non-ROM, and backed by a RAMBlock.
- Rejects memory backends with their own preallocation enabled; virtio-mem has its own `prealloc` property.
- Validates NUMA node, rejects mlock, validates block/requested/address/backend-size alignment, and requires coordinated RAM discard.
- Initializes all backend memory as discarded except during incoming migration.
- Chooses `unplugged-inaccessible` automatically for legacy x86 guests based on whether the backend has a reliable shared zero page; non-legacy targets force it on.

Properties and QOM interfaces:
- Properties include address, NUMA node, prealloc, memory backend link, early migration, dynamic memslots, and legacy-target `unplugged-inaccessible`.
- Runtime properties expose current size, requested size, and block size.
- Requested size can change after realize if aligned and not larger than backend size; changes resize the usable region and trigger virtio config notification.
- Implements `TYPE_RAM_DISCARD_MANAGER`.

Reset and unplug:
- A dedicated `VirtioMemSystemReset` resettable object handles system reset, not simple device reset.
- Normal system resets attempt to unplug all memory; wakeup resets preserve plugged memory.
- Device unplug is allowed only when unplugged-inaccessible is on, current plugged size is zero, and requested size is zero.

Important invariants:
- Guest ranges must be block-size aligned, nonzero, non-overflowing, and within usable region.
- Plug/unplug operations are rejected while migration is busy.
- Bitmap state is updated after memory discard/populate operations and listener notifications succeed.
- `vmem->size` and size-change notifiers are updated only after successful state changes.
- Dynamic memslot deactivation occurs after bitmap state reflects unplugged blocks.
- Realize sets the memory region's discard manager before the region is exposed to address spaces.

Filesystem/block relevance:
- No block-device protocol is implemented, but this file controls guest RAM availability and discard/populate state. That can materially affect filesystem cache contents, memory hotplug behavior, and migration of workloads using virtual storage.

Notable risks:
- Plug can fail due to preallocation or listener errors and must discard any memory that may have been populated.
- Unplug depends on backend discard support; failures are reported as busy.
- Legacy `unplugged-inaccessible=off` is tolerated only for compatibility and blocks device unplug.
- Migration ordering is delicate because unplugged memory must not be migrated with stale or accidentally populated content.
