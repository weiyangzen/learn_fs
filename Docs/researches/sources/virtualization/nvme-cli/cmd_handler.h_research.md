# File Research: sources/virtualization/nvme-cli/cmd_handler.h

- Purpose: multi-pass macro expansion framework for nvme-cli command plugins.
- Stage 1: emits static function prototypes for each `ENTRY`.
- Stage 2: emits `struct command` instances, supporting optional aliases through `ENTRY_W_ALIAS`/`ENTRY_WO_ALIAS`.
- Stage 3: builds a `commands[]` array of command pointers.
- Stage 4: constructs a `struct plugin` and registers it from a constructor function via `register_extension(&plugin)`.
- Dependency: repeatedly includes `CMD_INCLUDE(CMD_INC_FILE)` with different macro definitions.
