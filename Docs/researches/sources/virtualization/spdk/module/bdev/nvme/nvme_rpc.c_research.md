# File Research: sources/virtualization/spdk/module/bdev/nvme/nvme_rpc.c

This file implements the raw NVMe command passthrough RPC `bdev_nvme_send_cmd`. It allows callers to submit base64-encoded NVMe admin or I/O commands to a named NVMe bdev controller and returns a base64-encoded completion plus optional controller-to-host data and metadata.

The request context stores controller name, command type, data direction, timeout, data/metadata lengths, decoded command buffer, DMA data buffer, DMA metadata buffer, and response strings. Command buffers must decode to exactly `sizeof(struct spdk_nvme_cmd)`. Data and metadata can be supplied either as lengths, base64 payloads, or both; when both are present the decoded length must match the explicit length. Buffers are allocated with SPDK DMA allocation and at least 4 KiB for data.

Admin commands call `spdk_nvme_ctrlr_cmd_admin_raw()` on the underlying controller. I/O commands obtain an I/O channel for the controller, resolve its qpair through `bdev_nvme_get_io_qpair()`, and call `spdk_nvme_ctrlr_cmd_io_raw_with_md()`. The completion callback releases the I/O channel if one was acquired, encodes the NVMe completion, and encodes data/metadata only for controller-to-host transfers.

Errors in decode, controller lookup, allocation, submission, or response construction produce JSON-RPC errors and free the temporary context. The `timeout_ms` field is decoded and passed through the helper signatures, but the local submit wrappers do not apply it directly; timeout behavior depends on the lower NVMe/bdev module configuration.
