# File Research: sources/virtualization/spdk/lib/vfio_user/host/vfio_user.c

This file implements the client-side vfio-user socket protocol used by SPDK’s vfio-user PCI host wrapper.

`vfio_user_write()` sends a vfio-user header plus payload over a Unix socket with optional file descriptors through `SCM_RIGHTS`. It retries `sendmsg()` on `EINTR`, uses `MSG_NOSIGNAL`, and asserts the fd count fits `VFIO_MAXIMUM_SPARSE_MMAP_REGIONS`.

`read_fd_message()` receives the fixed header and any ancillary file descriptors with `recvmsg()`, rejects truncated control/data messages, and copies received fds into the request object. `vfio_user_read()` reads the header first, checks vfio-user error flags, then reads any remaining payload bytes with `read()`.

`vfio_user_dev_send_request()` is the central request/response helper. It builds a `vfio_user_request`, copies an argument payload up to 4096 bytes, sends DMA map/unmap requests with fds when supplied, waits for a mandatory reply, validates reply payload size, copies response payload back into the caller buffer for non-DMA-map requests, and returns any received fds for region-info replies.

`vfio_user_check_version()` negotiates vfio-user version 0.1. `vfio_user_get_dev_region_info()` and `vfio_user_get_dev_info()` issue device info queries. `vfio_user_dev_dma_map_unmap()` sends DMA map/unmap messages using the SPDK memory region’s IOVA, size, file offset, and fd. `vfio_user_dev_mmio_access()` allocates a variable-length region access message for region reads/writes and copies read data back.

`vfio_user_dev_setup()` opens an `AF_UNIX` stream socket, sets `FD_CLOEXEC`, validates the socket path length, connects to `dev->path`, stores the fd, and verifies protocol version.

Important invariants are the fixed maximum payload size, fd-passing limits, one request followed by one mandatory reply, and correct distinction between DMA requests that send fds and query requests that receive fds.
