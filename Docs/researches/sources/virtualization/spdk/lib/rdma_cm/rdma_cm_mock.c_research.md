# File Research: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_mock.c

This file implements a mock RDMA CM backend for builds configured without functional RDMA CM support. It exports the same `spdk_rdma_cm_*` symbols as the CMA backend but returns unsupported behavior.

Most APIs set `errno = ENOTSUP` and return `-1` or `NULL`: event channel creation, ID create/destroy, option setting, bind/resolve/connect/listen/accept/reject/disconnect, event get/ack, QP creation, QP attr init, establish, and device enumeration. Destroy-style void functions for event channels, QPs, and device lists are no-ops. Source and destination port getters return zero.

The file is useful for compile/link compatibility while making runtime RDMA CM usage fail explicitly. Callers must not assume a mock build can progress beyond feature detection or error paths.
