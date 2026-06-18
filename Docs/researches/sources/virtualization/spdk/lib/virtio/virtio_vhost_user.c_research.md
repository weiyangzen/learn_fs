# File Research: sources/virtualization/spdk/lib/virtio/virtio_vhost_user.c

## Purpose
Implements the client-side vhost-user backend for SPDK `virtio_dev`, connecting a virtio initiator to a vhost-user UNIX socket, negotiating features/protocol features, sharing hugepage memory, setting up vrings/eventfds, and forwarding config/status operations.

## Key Elements
`struct virtio_user_dev` stores the vhost socket fd, per-queue call/kick eventfds, queue size, cached virtio status, socket path, negotiated protocol features, vring addresses, and an SPDK memory map.

`vhost_user_write` and `vhost_user_read` send and receive vhost-user messages, including SCM_RIGHTS file descriptor passing. `vhost_user_sock` formats each supported request type, attaches memory-region fds/eventfds when needed, sends the message, closes temporary hugepage fds after `SET_MEM_TABLE`, and parses replies for feature, queue number, vring base, and config requests.

Memory sharing scans `/proc/self/maps` for DPDK hugepage files named like `map_<n>`, merges adjacent mappings from the same path, opens those files, and sends them as vhost-user memory regions with virtual addresses used for both guest physical and userspace addresses. Dynamic memory-map changes are rejected while the device is active except during initial registration or stop.

Device startup negotiates multi-queue limits, creates per-queue call fds, registers memory, and sends vring size/base/address/kick messages. Queue setup allocates vring memory, creates call/kick eventfds, optionally sends `SET_VRING_ENABLE`, and records descriptor/avail/used virtual addresses. Queue notify writes to the kick eventfd.

Feature setup sends `SET_FEATURES`, records negotiated features, sets `modern` if `VIRTIO_F_VERSION_1` is present, and if protocol features are negotiated, intersects host features with `MQ` and `CONFIG` support before sending `SET_PROTOCOL_FEATURES`.

Config read/write use `GET_CONFIG` and `SET_CONFIG` only if `VHOST_USER_PROTOCOL_F_CONFIG` was negotiated. Status changes start the backend when DRIVER_OK is set and stop it on reset from DRIVER_OK.

## Dependencies
Depends on UNIX sockets, `eventfd`, `sendmsg`/`recv`, `/proc/self/maps`, SPDK string/config/util/mem_map APIs, and vhost-user protocol definitions in `spdk_internal/vhost_user.h`.

## Behavior/Risks
This code assumes Linux-style `/proc/self/maps` and DPDK hugepage file naming. It does not support dynamic memory allocation while active; applications must preallocate memory.

The vhost-user read path expects exact header/payload sizes and exact reply flags. Short reads return busy/error. Unsupported protocol features are silently masked to the two features this backend supports.

When the host lacks multi-queue support or offers fewer queues than requested, `vdev->max_queues` is reduced. The warning path subtracts fixed queues in messages, so fixed/control queues matter for interpreting queue counts.
