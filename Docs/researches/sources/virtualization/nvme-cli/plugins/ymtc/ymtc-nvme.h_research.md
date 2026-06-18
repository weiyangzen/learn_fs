# File Research: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.h

Command registration header for the YMTC vendor plugin.

Key elements:
- Sets `CMD_INC_FILE` to `plugins/ymtc/ymtc-nvme`.
- Defines plugin name `ymtc` with description `Ymtc vendor specific extensions`.
- Registers one command: `smart-log-add`, mapped to `get_additional_smart_log`.
- Includes the common command registration machinery and `define_cmd.h`.

Dependencies:
- Consumed by `ymtc-nvme.c` under `CREATE_CMD`.
