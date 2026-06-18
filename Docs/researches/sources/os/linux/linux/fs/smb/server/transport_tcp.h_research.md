# File Research: sources/os/linux/linux/fs/smb/server/transport_tcp.h

Declares TCP transport setup, lookup, teardown, and interface configuration APIs.

Key contents:
- Interface-list configuration from startup IPC.
- Lookup of configured interface by netdevice name.
- Transport free helper.
- TCP init/destroy lifecycle functions.

Role in subsystem:
- Small public surface connecting server startup/shutdown and netdevice management to the TCP transport implementation.
