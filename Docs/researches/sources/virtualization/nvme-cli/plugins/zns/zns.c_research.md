# File Research: sources/virtualization/nvme-cli/plugins/zns/zns.c

Implements the Zoned Namespace Command Set plugin.

Key command areas:
- `list`: scans libnvme topology and displays namespaces whose sysfs `queue/zoned` attribute is `host-managed`.
- `id-ctrl`: issues ZNS Identify Controller via admin passthrough and prints in selected output format.
- `id-ns`: identifies base namespace and ZNS namespace data, then prints combined ZNS namespace information.
- Zone management send wrappers: reset, close, finish, open, offline, set descriptor extension, ZRWA flush, and generic `zone-mgmt-send`.
- Zone management receive and report paths: `zone-mgmt-recv`, `report-zones`, and `changed-zone-list`.
- `zone-append`: reads data/metadata from files or stdin, validates LBA/metadata alignment, sets command control flags, issues append, and optionally prints latency.

Important behaviors:
- Defaults namespace ID from the opened device when `--namespace-id` is omitted.
- Computes zone descriptor extension bytes from ZNS identify namespace data using active LBA format.
- `report_zones` first reads total zone count, allocates huge memory for chunked zone reports, then iterates chunks using zone size to advance offsets.
- Uses nvme-cli output flag validation and JSON/list helpers for formatted output.
- Uses cleanup attributes for libnvme contexts and allocated buffers where available.

Dependencies:
- Uses libnvme admin and IO passthrough initializers for ZNS commands.
- Uses `nvme-print` ZNS display functions and nvme-cli argument parser macros.

Notes:
- `zone_append` calls `libnvme_exec_admin_passthru` after initializing a ZNS append command; append is an I/O command, so this is a point worth checking against current libnvme expectations.
- Metadata buffer allocation uses `meta_size` while reading `cfg.metadata_size`; if metadata size can exceed one metadata element, this path deserves scrutiny.
