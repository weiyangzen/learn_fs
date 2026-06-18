# File Research: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.c

Seagate vendor-specific nvme-cli plugin implementation. It exposes log discovery, SMART/temperature/PCIe/fw-history reporting, telemetry dumping, clear operations, and plugin version commands.

Key command handlers:
- `log_pages_supp`: retrieves vendor log `0xc5` and prints supported log pages in normal or JSON format.
- `vs_smart_log`: identifies controller model, branches for legacy Jaguar/Panthor devices, reads extended SMART log `0xc4` plus DRAM supercap log `0xcf`, or legacy SMART health log `0xc0`.
- `temp_stats`: combines standard SMART temperature sensors with extended SMART max-temperature attributes and supercap temperature from `0xcf`.
- `vs_pcie_error_log`: reads `0xcb`, computes correctable/uncorrectable totals, and prints detailed PCIe error counters.
- `stx_vs_fw_activate_history`: reads firmware activation history from `0xc2`.
- `clear_fw_activate_history`: for legacy models, sends set-feature `0xc1` with `0x80000000`.
- `vs_clr_pcie_correctable_errs`: clears PCIe counters via feature `0xe1`/log `0xcb` for non-legacy and feature `0xc3` for legacy, then unconditionally sends the `0xe1` clear path again.
- `get_host_tele`: retrieves telemetry host-initiated log `0x07`, optionally with capture bit encoded into the log identifier.
- `get_ctrl_tele`: retrieves telemetry controller-initiated log `0x08`.
- `vs_internal_log`: dumps controller telemetry `0x08` as binary to stdout or a file.
- `seagate_plugin_version` and `stx_ocp_plugin_version`: print plugin version numbers.

Important helpers:
- `log_pages_supp_print`: maps Seagate/OCP/vendor log IDs to human names.
- `stx_is_jag_pan`: checks controller model against the legacy model table in `seagate-diag.h`.
- `smart_attribute_vs`: interprets SMART raw values differently depending on extended SMART version.
- Multiple JSON/human print helpers for SMART, DRAM supercap, C0 health, PCIe errors, and firmware history.
- `seaget_d_raw`: writes binary buffers to a file descriptor.

Notable behavior:
- `vs_smart_log` first branches on legacy model, but then proceeds to retrieve `0xc4`/`0xcf` again after the branch. This means some devices may get duplicate extended SMART output or extra log reads.
- Several JSON paths allocate root objects but not all paths free them consistently.
- `json_stx_vs_fw_activate_history` prints timestamp text to stdout while constructing JSON, causing mixed output.
- Telemetry retrieval reads the header first, then iterates in `TELEMETRY_BLOCKS_TO_READ` chunks of 512-byte blocks using `libnvme_get_log` with log page offset.
- File output in `vs_internal_log` uses `O_WRONLY | O_CREAT` without `O_TRUNC`, so old longer files can retain trailing data.

External dependencies:
- libnvme standard get-log, get-feature, set-feature, identify.
- nvme-cli JSON and hexdump helpers.
- Seagate packed ABI structures from `seagate-diag.h`.
