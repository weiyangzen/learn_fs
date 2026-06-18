# File Research: sources/virtualization/qemu/hw/virtio/vhost-user.c

## Purpose
Implements QEMU's vhost-user backend operations: protocol messages, memory table sharing, vring setup, backend request handling, migration/postcopy support, device config, crypto sessions, inflight descriptors, shared objects, and device-state migration.

## Protocol and Message Layer
- Defines frontend requests from `VHOST_USER_GET_FEATURES` through `VHOST_USER_CHECK_DEVICE_STATE`.
- Defines backend requests for IOTLB, config change, host notifier, and shared-object add/remove/lookup.
- Defines packed protocol payload structures for memory regions, memory add/remove, log sharing, config space, crypto sessions, vring areas, inflight state, shared objects, and device-state transfer.
- Reads and validates reply headers, protocol version flags, payload sizes, and expected request types.
- Writes messages with optional SCM_RIGHTS file descriptors through the chardev.
- Suppresses per-device requests on secondary `vhost_dev` instances when a virtio device is represented by multiple vhost devices.
- Implements reply-ack processing through `VHOST_USER_NEED_REPLY_MASK`.

## Memory and Postcopy
- Builds `VHOST_USER_SET_MEM_TABLE` messages by translating QEMU host addresses to memory regions, file descriptors, and mmap offsets.
- Tracks shadow memory regions so backends supporting `VHOST_USER_PROTOCOL_F_CONFIGURE_MEM_SLOTS` can receive incremental add/remove messages.
- Maintains RAMBlock and offset arrays needed for postcopy fault translation.
- Handles postcopy-specific memory table replies, backend client base addresses, and final acknowledgements.
- Registers a Linux userfaultfd postcopy handler that maps backend fault addresses back to RAMBlocks and requests pages.
- Provides a postcopy waker that wakes backend mappings when pages arrive.
- Implements postcopy advise, listen, and end protocol messages through migration notifiers.

## Vring and Notifier Handling
- Sends vring num/base/addr/endian/enable messages.
- Waits for backend replies where ordering matters, such as queue enablement and logging.
- Sends kick/call/error eventfds and waits for reply-ack when supported to avoid interrupt loss during fd replacement.
- Handles backend host-notifier messages by mapping a page-sized fd and installing it as a virtio host notifier memory region.
- Removes host notifier mappings with RCU-safe cleanup.

## Backend Request Channel
- Creates a socketpair for backend-initiated requests when `VHOST_USER_PROTOCOL_F_BACKEND_REQ` is negotiated.
- Handles backend IOTLB messages, config-change messages, host notifier updates, and shared-object operations.
- Sends backend request replies when requested or when shared-object lookup requires a response.

## Feature Negotiation and Lifecycle
- Initializes backend state by querying features and protocol features.
- Negotiates only QEMU-supported protocol bits and suppresses unsupported config or inflight features.
- Validates queue count, IOMMU requirements, RAM slot limits, and migration logging support.
- Sets a migration blocker when the backend lacks shared-memory dirty logging.
- Registers cleanup for backend channel, postcopy notifiers, postcopy fds, and tracked RAMBlock arrays.
- Exposes memory slot limit, private memslot policy, vq index mapping, device start status, reset status, and migration-done RARP behavior through `user_ops`.

## Device Services
- Gets and sets virtio config space through `VHOST_USER_GET_CONFIG` and `VHOST_USER_SET_CONFIG`.
- Sends device IOTLB messages with reply acknowledgement.
- Creates and closes vhost-user crypto sessions, copying bounded symmetric/asymmetric key material into protocol payloads.
- Gets and sets inflight shared-memory fds for inflight descriptor migration.
- Supports shared object lookup, including DMABUF forwarding and delegating lookup through another vhost device.
- Transfers backend device migration state using `SET_DEVICE_STATE_FD` and validates completion with `CHECK_DEVICE_STATE`.
- Provides `vhost_user_init()`, `vhost_user_cleanup()`, and deferred asynchronous close handling for devices using this backend.

## Filesystem/Storage Relevance
This is the central QEMU implementation used by vhost-user storage and filesystem devices such as vhost-user-blk, vhost-user-scsi, and virtio-fs. It controls how guest memory is shared with external daemons, how virtqueues are wired to eventfds, how IOMMU misses are serviced, and how backend state is migrated.
