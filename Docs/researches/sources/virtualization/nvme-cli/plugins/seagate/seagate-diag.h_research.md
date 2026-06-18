# File Research: sources/virtualization/nvme-cli/plugins/seagate/seagate-diag.h

Seagate diagnostic layout header for vendor-specific nvme-cli plugin commands.

Main contents:
- Plugin version constants: Seagate `1.2`, OCP Seagate `1.0`.
- Persistent log and chunk sizes used by diagnostic retrieval.
- `stx_jag_pan_mn`: static list of 123 legacy Jaguar/Panthor model numbers used by `stx_is_jag_pan` to choose legacy log behavior.
- Supported log page map types: `log_page_map_entry` and `log_page_map`, matching a 4 KiB vendor log directory payload.
- Extended SMART types:
  - `SmartVendorSpecific`
  - `EXTENDED_SMART_INFO_T`
  - `vendor_smart_attribute_data`
  - `STX_EXT_SMART_LOG_PAGE_C0`
  - `vendor_log_page_CF`
- Telemetry header `nvme_temetry_log_hdr`, used for host/controller telemetry dumping.
- PCIe error log layout `pcie_error_log_page`.
- Firmware activation history layouts `stx_fw_activ_his_ele` and `stx_fw_activ_history_log_page`.
- Enumerations for Seagate extended SMART attribute indexes and vendor SMART attribute IDs.

Notable role:
- This header is not just declarations; it defines large static data and packed firmware ABI structs. It is coupled tightly to `seagate-nvme.c` parsing/printing logic.
- It declares `seaget_d_raw`, implemented in `seagate-nvme.c`.
