# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/av1394/av1394_impl.h

This private target-driver header defines the `av1394` IEC 61883 audio/video driver internals.

Main utilities:
- `AV_SWAP16` and `AV_SWAP32` perform endian conversion on little-endian systems.
- `av1394_list_item_t` and `av1394_list_t` implement an intrusive double-linked list.
- `av1394_queue_t` wraps an mblk list with mutex, size/max accounting, and condition variable; `AV1394_ENTERQ/LEAVEQ` lock helpers access it.

Async/FCP/config-ROM state:
- `av1394_fcp_cmd_t`: one outgoing FCP command/response slot with busy and transmit condition variables.
- `av1394_fcp_t`: per-instance FCP command and response slots.
- FCP ARQ max length is `0x200`.
- Config ROM address constants for bus name and EUI64 fields.
- Text-leaf, parsed-directory, parse-argument, and config-ROM parser state structures, with max parse depth 5.
- `av1394_async_cmd_t`: mutex-protected async command wrapper.
- `av1394_async_t`: async module state including open count/flags, target info, bus generation, FCP/config-ROM modules, read queue, pollhead, and poll events.

Device state:
- `av1394_dev_state_t` models init, online, suspended, and disconnected states with attach/detach/reconnect/disconnect/CPR transitions documented in comments.
- `av1394_inst_t`: per-instance soft state containing lock, dip, instance, current/previous device states, t1394 attach info/handle, async and isoch modules, and DDI callback IDs.

Minor-device mapping:
- High minor bit distinguishes async from isoch nodes.
- Macros convert instance to async/isoch minor and minor back to instance/type.

Function prototypes:
- List and queue operations.
- FCP attach/detach/open/close/write.
- Config ROM init/fini/close and ioctl helpers for bus name, UID, and text leaf.
- Async attach/detach/CPR/bus reset/disconnect/reconnect/open/close/read/write/ioctl/poll/read-queue insertion.

Research notes:
- The header relies on `av1394_isoch.h` for the isochronous module state embedded in `av1394_inst_t`.
- Queue and async structures are annotated with mutex protection, while immutable attach-time fields are readable without lock.
