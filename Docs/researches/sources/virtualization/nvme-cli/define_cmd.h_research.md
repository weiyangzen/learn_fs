# File Research: sources/virtualization/nvme-cli/define_cmd.h

This header is a macro include shim used during command declaration generation.

Core behavior:
- Only active when `CREATE_CMD` is already defined.
- Temporarily undefines `CREATE_CMD`.
- Defines stringify helpers and `CMD_INCLUDE(cmd)` to include `<cmd>.h` based on `CMD_INC_FILE`.
- Defines `CMD_HEADER_MULTI_READ`, includes the command-specific header, includes `cmd_handler.h`, then undefines `CMD_HEADER_MULTI_READ`.
- Restores `CREATE_CMD`.

Integration role:
- Supports multi-pass command macro expansion in nvme-cli.
- Keeps command header inclusion parameterized by `CMD_INC_FILE`.
