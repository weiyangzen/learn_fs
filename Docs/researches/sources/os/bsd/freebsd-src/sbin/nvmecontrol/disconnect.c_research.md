# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/disconnect.c

Implements NVMe over Fabrics disconnect commands.

Key behaviors:
- `disconnect` accepts controller ID, namespace ID, or SubNQN.
- If the argument is a valid NQN, passes it directly to `nvmf_disconnect_host()`.
- Otherwise opens the device, resolves the controller path/SubNQN via `get_nsid()`, and disconnects that host connection.
- `disconnect-all` calls `nvmf_disconnect_all()`.

Research notes:
- This file delegates actual disconnect logic to libnvmf/kernel interfaces.
