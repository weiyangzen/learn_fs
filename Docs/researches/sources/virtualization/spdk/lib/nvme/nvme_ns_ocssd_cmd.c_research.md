# File Research: sources/virtualization/spdk/lib/nvme/nvme_ns_ocssd_cmd.c

This file implements namespace-level Open-Channel SSD vector commands.

`spdk_nvme_ocssd_ns_cmd_vector_reset()` validates an LBA list with 1 to `SPDK_NVME_OCSSD_MAX_LBAL_ENTRIES` entries, allocates a null request, sets opcode `SPDK_OCSSD_OPC_VECTOR_RESET` and NSID, optionally puts chunk-info physical address in MPTR, encodes either the single LBA directly in CDW10/11 or the physical address of the LBA list for multiple entries, sets zero-based LBA count in CDW12, and submits.

`_nvme_ocssd_ns_cmd_vector_rw_with_md()` is shared by vector read/write variants. It permits only `SPDK_OCSSD_IO_FLAGS_LIMITED_RETRY`, validates data buffer and LBA list/count, allocates a request, initializes contiguous data and optional metadata transfer sizes as `num_lbas * sector_size` and `num_lbas * md_size`, fills opcode/NSID, encodes single-LBA or LBA-list physical address in CDW10/11, stores zero-based count and flags in CDW12, and submits.

Public wrappers provide vector write/read with and without metadata by passing either `SPDK_OCSSD_OPC_VECTOR_WRITE` or `SPDK_OCSSD_OPC_VECTOR_READ`.

`spdk_nvme_ocssd_ns_cmd_vector_copy()` validates source and destination LBA lists, count, and limited-retry flags. It builds a no-payload vector copy command, encoding either single source/destination LBAs directly or physical addresses of source/destination LBA lists in CDW10/11 and CDW14/15, then sets zero-based count plus flags in CDW12.

The file depends on callers providing physically addressable LBA-list and chunk-info memory because it uses `spdk_vtophys()` directly. It also assumes namespace sector and metadata sizes are already populated by normal namespace identify processing.
