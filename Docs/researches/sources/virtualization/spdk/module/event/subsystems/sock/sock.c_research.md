# File Research: sources/virtualization/spdk/module/event/subsystems/sock/sock.c

Registers SPDK socket initialization as an event subsystem.

Key elements:
- Initializes socket implementations with interrupt mode status from `spdk_interrupt_mode_is_enabled()`.
- Allows default socket implementation override via `SPDK_SOCK_IMPL_DEFAULT`.
- Writes socket config JSON through `spdk_sock_write_config_json()`.
- Registers subsystem name `sock`.

Dependencies:
- SPDK sock module internals, init, thread, string, and log APIs.

Research notes:
- Fini immediately advances the subsystem chain; shutdown logic is owned by socket implementation modules.
