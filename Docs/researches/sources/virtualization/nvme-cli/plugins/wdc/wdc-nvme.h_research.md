# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.h

Registers the `wdc` plugin.

Key details:
- Plugin version: `2.15.0`.
- Uses nvme-cli command registration macros.

Commands include:
- Diagnostics and dumps: `cap-diag`, `drive-log`, `get-crash-dump`, `get-pfail-dump`, `drive-essentials`.
- Device operations: `id-ctrl`, `purge`, `purge-monitor`, `drive-resize`, `namespace-resize`.
- Vendor logs: `vs-internal-log`, `vs-nand-stats`, `vs-smart-add-log`, `vs-drive-info`, `vs-temperature-stats`, `vs-pcie-stats`, `vs-cloud-log`, `vs-hw-rev-log`, `cu-smart-log`.
- OCP/cloud-related logs: firmware activation history, telemetry controller option, error reason identifier, log page directory, latency monitor, error recovery, device capabilities, unsupported requirements, cloud boot SSD version.
- Control commands: clear PCIe correctable errors, clear assert dump, clear firmware activation history, set latency monitor feature.
- Derived metric: `vs-device-waf`.

Risks/notes:
- Command description for `vs-device-waf` has typo `"Amplication"`.
- Command description for namespace resize says `"NamespaceDrive Resize"`.
