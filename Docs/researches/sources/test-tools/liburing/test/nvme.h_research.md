# sources/test-tools/liburing/test/nvme.h

Purpose: helper header for tests that issue NVMe io_uring passthrough commands and need namespace geometry.

Important APIs/types/functions: fallback `struct nvme_uring_cmd`, `NVME_URING_CMD_IO`, `NVME_URING_CMD_IO_VEC`, `struct nvme_id_ns`, `struct nvme_lbaf`, `nvme_get_info`, `NVME_IOCTL_ID`, `NVME_IOCTL_ADMIN_CMD`, `nvme_admin_identify`, `nvme_cmd_read`, `nvme_cmd_write`, `ilog2`, and globals `nsid`, `lba_shift`, `meta_size`.

Control flow: `nvme_get_info()` opens an NVMe device, obtains the namespace id via ioctl, sends an identify admin command, derives LBA size/shift and metadata size from the active LBA format, then closes the fd.

State and persistence behavior: stores namespace id, LBA shift, and metadata size in static globals for later test code. It does not write to the device.

Dependencies and integration points: depends on `<linux/nvme_ioctl.h>` and supplies local uring command definitions when system headers lack them. Intended for inclusion by NVMe passthrough tests.

Risks and test signals: ioctl failures return negative errno or raw admin error, causing callers to skip/fail device tests. Header ABI compatibility is critical for older distro headers.
