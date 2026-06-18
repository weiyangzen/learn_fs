# File Research: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.h

SED Opal command header. It declares prompts, password length limits, global option flags, command enum values, and implementation functions.

Key definitions:
- Password prompts for current, new, re-entered, and PSID inputs.
- `SEDOPAL_MIN_PASSWORD_LEN` 8 and `SEDOPAL_MAX_PASSWORD_LEN` 32.
- `NVME_DEV_PATH` set to `/dev/nvme`, though this file’s listed implementation path does not use an opener by that name.
- `enum sedopal_cmds` for initialize, lock, unlock, revert, password, discover.

Declared APIs:
- Command functions: initialize, lock, unlock, revert, password, discover.
- Utility functions: `sedopal_open_nvme_device`, `sedopal_lock_unlock`, `sedopal_error_to_text`, `sedopal_locking_state`.

Note: `sedopal_open_nvme_device` is declared here but not implemented in the listed `.c` file.
