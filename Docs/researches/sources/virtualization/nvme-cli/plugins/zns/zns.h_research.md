# File Research: sources/virtualization/nvme-cli/plugins/zns/zns.h

Command registration header for the ZNS plugin.

Key elements:
- Sets `CMD_INC_FILE` to `plugins/zns/zns`.
- Registers plugin name `zns` with description `Zoned Namespace Command Set`.
- Registers ZNS commands including list, identify controller/namespace, report zones, zone reset/close/finish/open/offline, descriptor extension, ZRWA flush, changed zone list, management send/receive, and zone append.
- Includes `define_cmd.h` for command table generation.

Dependencies:
- Consumed by `zns.c` under `CREATE_CMD`.
