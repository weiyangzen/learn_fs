# File Research: sources/virtualization/spdk/lib/init/subsystem.h

`subsystem.h` is the private header for init subsystem internals. It declares subsystem lookup/iteration helpers, dependency iteration helpers, and `subsystem_config_json()`.

The header allows RPC/config files to inspect registered subsystems without exposing the global TAILQs directly. `subsystem_config_json()` writes one subsystem’s configuration to a JSON writer, falling back to JSON null when no config writer exists.

Research notes: this file is the small internal ABI between `subsystem.c`, `subsystem_rpc.c`, and other init code.
