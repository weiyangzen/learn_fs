# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme-cmds.h

Declares run-level WDC command functions and capability helpers.

Command declarations include:
- Cloud SSD plugin/version commands.
- Internal firmware log.
- NAND stats.
- Additional SMART.
- PCIe correctable error clearing.
- Drive status, resize, namespace resize.
- Firmware activation history.
- Telemetry controller option and reason identifier.
- Log page directory.
- PCIe stats, latency monitor, OCP-style logs, cloud log, hardware revision, WAF, temperature stats, customer unique SMART.

Helper declarations:
- `run_wdc_nvme_check_supported_log_page()`
- `run_wdc_get_fw_cust_id()`
- `run_wdc_get_drive_capabilities()`

Risks/notes:
- Does not include the types it references; consumers must include command/plugin/libnvme type definitions first.
- `run_wdc_cloud_ssd_plugin_version()` is declared twice.
