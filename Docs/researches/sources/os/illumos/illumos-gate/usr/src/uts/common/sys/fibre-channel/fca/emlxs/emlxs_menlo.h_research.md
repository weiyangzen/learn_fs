# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_menlo.h

## Purpose

Defines the Menlo management protocol used when `MENLO_SUPPORT` is enabled. Menlo appears to be a sideband/FCoE management firmware component for Emulex adapters, covering initialization, firmware download, memory access, forwarding table entries, FCoE mode/configuration, DCB/PFC priority groups, stats, logs, diagnostics, FCF/FACL state, and firmware image metadata.

## Main Definitions

### Commands

Command structures include:

- `menlo_init_cmd_t`
- `menlo_fw_download_cmd_t`
- `menlo_memory_cmd_t`
- `menlo_fte_insert_cmd_t`
- `menlo_fte_delete_cmd_t`
- `menlo_get_cmd_t`
- `menlo_set_cmd_t`
- `menlo_loopback_cmd_t`
- `menlo_reset_cmd_t`
- `menlo_fru_data_cmd_t`
- `menlo_diag_cmd_t`
- Hornet 2/FCoE extensions such as `fip_params_t`, `non_fip_params_t`, `menlo_fcoe_params_t`, `menlo_set_fcoe_params_cmd_t`, `set_facl_cmd_t`, `facl_t`, `fcf_id_t`, `create_vl_cmd_t`, `delete_vl_cmd_t`, `menlo_pg_info_t`, `menlo_set_pg_info_cmd_t`, and `menlo_set_host_eth_pfc_flag_t`.

`menlo_cmd_t` is the command union and defines command codes such as `MENLO_CMD_INITIALIZE`, `MENLO_CMD_FW_DOWNLOAD`, `MENLO_CMD_GET_CONFIG`, `MENLO_CMD_GET_PORT_STATS`, `MENLO_CMD_SET_FCOE_PARAMS`, `MENLO_CMD_GET_FCF_LIST`, `MENLO_CMD_SET_FACL`, `MENLO_CMD_CREATE_VL`, `MENLO_CMD_SET_PG`, and Zephyr-specific reset/mode commands.

### Responses

Response structures include:

- `menlo_init_rsp_t`
- `menlo_get_config_rsp_t`
- `menlo_fc_stats_rsp_t`
- `menlo_network_stats_rsp_t`
- `menlo_lif_stats_rsp_t`
- `menlo_asic_stats_rsp_t`
- `menlo_log_config_rsp_t`
- `menlo_log_data_rsp_t`
- `menlo_panic_log_data_rsp_t`
- `menlo_lb_mode_rsp_t`
- `menlo_ftable_rsp_t`
- `menlo_sfp_rsp_t`
- `menlo_fru_data_rsp_t`
- `menlo_diag_log_data_rsp_t`
- `menlo_diag_log_t`
- `menlo_diag_log_entry_t`
- Hornet 2/FCoE responses such as `menlo_get_fcoe_params_rsp_t`, `fcf_info_t`, `menlo_get_fcf_list_rsp_t`, `menlo_get_facl_rsp_t`, `create_vl_rsp_t`, `menlo_get_pg_info_rsp_t`, `menlo_get_host_eth_pfc_flag_rsp_t`, and `menlo_get_dcbx_mode_rsp_t`.

`menlo_rsp_t` is the response union and defines Menlo response/error codes including success, generic failure, invalid command/credit/size/address/context/length/type/data/value/mask/checksum, unknown FCID/WWN, busy, invalid flag, and SFP absent.

### Firmware Image Metadata

Defines:

- `menlo_image_hdr_t`
- `menlo_version_hdr_t`

These describe image length, payload length, checksum offset, padding, image type, version, and checksum.

## Integration Notes

All substantive content is guarded by `#ifdef MENLO_SUPPORT`. If that macro is not enabled, this header contributes only include guards and C++ linkage.

The protocol uses fixed-width integers for most command/response fields and many `uint32_t data` fields to represent variable trailing arrays or offsets.

## Risks and Gotchas

- Duplicate macro names such as `FCOE_MODE_NON_FIP`, `FCOE_MODE_FIP`, `SPMA_ADDR_MODE`, and `FPMA_ADDR_MODE` are defined in more than one structure block with identical meanings; edits must avoid conflicting redefinitions.
- Several response payloads expose very large stats structures; consumers must size buffers according to command response length, not just `menlo_rsp_t`.
- Log and diagnostic response structures encode trailing arrays through scalar `data` fields, so parsing code must handle variable payloads carefully.
- Menlo command and response unions are not self-validating; callers must match `code` with the correct union member.
