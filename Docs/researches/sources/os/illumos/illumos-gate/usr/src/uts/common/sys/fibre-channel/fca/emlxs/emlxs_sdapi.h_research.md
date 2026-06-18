# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_sdapi.h

## Purpose

Defines the SAN Diagnostic API contract used between applications and `libdfc`, with structures and prototypes for latency collection and event registration.

## Main Definitions

### Latency Collection

- `SD_SCSI_IO_LATENCY_TYPE`
- `SD_IO_LATENCY_MAX_BUCKETS`
- `SD_time_stats_v0`
- `SD_IO_Latency_Response`
- `SD_SEARCH_LINEAR`
- `SD_SEARCH_POWER_2`

Defines return codes in `enum SD_RETURN_CODES`, including argument errors, invalid board/vport, unsupported category/subcategory/function, more data available, registration errors, memory errors, bucket not set, invalid search type, out of handles, library not initialized, and data collection active/inactive.

Declares APIs:

- `DFC_SD_Get_Granularity`
- `DFC_SD_Set_Bucket`
- `DFC_SD_Destroy_Bucket`
- `DFC_SD_Get_Bucket`
- `DFC_SD_Start_Data_Collection`
- `DFC_SD_Stop_Data_Collection`
- `DFC_SD_Reset_Data_Collection`
- `DFC_SD_Get_Data`

### Event Categories

Defines registration masks for ELS, fabric, SCSI, board, and adapter events. Defines valid subcategory masks for ELS, fabric, and SCSI event classes.

Event payload structures include:

- generic `sd_event`
- ELS wrappers and payloads: `sd_els_event_details_v0`, `sd_plogi_rcv_v0`, `sd_prlo_rcv_v0`, `sd_lsrjt_rcv_v0`, `sd_adisc_rcv_v0`
- fabric wrappers and payloads: `sd_fabric_event_details_v0`, `sd_pbsy_rcv_v0`, `sd_fcprdchkerr_v0`
- SCSI wrappers and payloads: `sd_scsi_event_details_v0`, `sd_scsi_generic_v0`, `sd_scsi_checkcond_v0`, `sd_scsi_varquedepth_v0`

Defines callback type `sd_callback` and registration APIs:

- `DFC_SD_RegisterForEvent`
- `DFC_SD_unRegisterForEvent`

## Integration Notes

This header references `HBA_WWN`, so it depends on HBA API types included earlier by consumers. It is explicitly intended for app/libdfc communication, not only kernel-internal use.

## Risks and Gotchas

- `struct sd_event` contains `size_t` and a raw `void *`, so it is not a stable cross-architecture serialized wire format without wrapping.
- Callback parameter name appears as `ort_id`, likely a typo for `port_id`; ABI is unaffected but generated docs or bindings may expose it.
- Event payload versions are embedded per structure, suggesting consumers should inspect version fields before decoding.
