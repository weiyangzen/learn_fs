# File Research: sources/virtualization/spdk/lib/nvme/nvme_zns.c

## Purpose
Provides the public SPDK NVMe Zoned Namespace helper APIs and command wrappers for ZNS operations.

## Main Responsibilities
- Exposes namespace and controller ZNS identify data through `spdk_nvme_zns_ns_get_data()` and `spdk_nvme_zns_ctrlr_get_data()`.
- Computes zone sizing and counts from namespace ZNS identify data and active LBA format.
- Returns max open zones, max active zones, and controller max zone append size.
- Wraps zone append commands, including metadata and vectored SGL variants.
- Builds Zone Management Receive commands for report and extended report operations.
- Builds Zone Management Send commands for close, finish, open, reset, offline, and set zone descriptor extension.

## Key Interfaces
- Uses lower-level internal command helpers such as `nvme_ns_cmd_zone_append_with_md()` and `nvme_ns_cmd_zone_appendv_with_md()`.
- Allocates NVMe requests with `nvme_allocate_request_user_copy()` or `nvme_allocate_request_null()`.
- Submits commands through `nvme_qpair_submit_request()`.

## Important Details
- Zone size in bytes is `zone_size_sectors * sector_size`.
- Zone report receive uses `SPDK_NVME_OPC_ZONE_MGMT_RECV`, sets SLBA in CDW10/CDW11, NUMD in CDW12, and report action/options in CDW13.
- Zone management send uses `SPDK_NVME_OPC_ZONE_MGMT_SEND`; when `select_all` is true it omits SLBA and sets the select-all bit in CDW13.
- `spdk_nvme_zns_set_zone_desc_ext()` validates nonzero payload size and non-null buffer before creating a host-to-controller copy request.

## Storage Relevance
This is the user-facing ZNS command layer for applications managing zone lifecycle, zone reports, zone append writes, and zone descriptor extensions over NVMe.

## Risks / Notes
- The helper assumes `ns->nsdata_zns` and active format index are valid for the namespace.
- Most validation is limited to obvious payload checks; device-level semantic errors are returned asynchronously through NVMe completions.
