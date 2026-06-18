# File Research: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_ocssd_cmd.c

This file provides controller-level Open-Channel SSD helpers.

`spdk_nvme_ctrlr_is_ocssd_supported()` gates support on `NVME_QUIRK_OCSSD`, then applies a CNEX Labs/QEMU-specific check: it finds the first active namespace, fetches namespace vendor-specific identify bytes, and returns true only when `vendor_specific[0] == 0x1`. The comment notes there is no standardized OCSSD detection rule and vendors may need different conditions.

`spdk_nvme_ocssd_ctrlr_cmd_geometry()` sends the OCSSD geometry admin command. It requires a non-null payload exactly sized as `struct spdk_ocssd_geometry_data`, allocates a user-copy admin request in controller-to-host direction, sets opcode `SPDK_OCSSD_OPC_GEOMETRY` and NSID, submits under `nvme_ctrlr_lock()`, and returns allocation or submission status.

The main dependencies are `spdk/nvme_ocssd.h`, controller quirks, namespace lookup, vendor-specific namespace data, and normal admin request submission. The detection path is intentionally heuristic; adding OCSSD device support likely means extending this vendor-specific logic.
