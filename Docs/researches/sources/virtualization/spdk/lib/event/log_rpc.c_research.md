# File Research: sources/virtualization/spdk/lib/event/log_rpc.c

Implements JSON-RPC methods for SPDK logging control.

Important RPCs:
- `log_set_print_level` and `log_get_print_level`
- `log_set_level` and `log_get_level`
- `log_set_flag`, `log_clear_flag`, and `log_get_flags`
- `log_enable_timestamps`

Important behavior:
- Converts internal log levels to strings: `ERROR`, `WARNING`, `NOTICE`, `INFO`, `DEBUG`.
- Uses generated decoder/free helpers for log-level and string parameters.
- Exposes startup/runtime control for most log settings; timestamp enablement is runtime-only.
- Registers the `log_rpc` log component.

Role: provides dynamic observability controls for SPDK applications without restart.
