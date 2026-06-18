# File Research: sources/virtualization/libblockdev/src/plugins/dm_logging.c

## Role

`dm_logging.c` adapts libdevmapper logging to libblockdev's logging utility.

## Behavior

`redirect_dm_log()` accepts libdevmapper's log callback arguments, formats the variadic message with `g_vasprintf()`, prefixes it with `[libdevmapper]`, and sends it to `bd_utils_log()`.

In debug builds, the log message includes source file and line. In non-debug builds, it only includes the libdevmapper message.

If libdevmapper supplies a log level above `LOG_DEBUG`, the code clamps it to debug.

## Dependencies

- GLib formatting and allocation.
- syslog log levels.
- libblockdev utility logging.

## Notable Risks

- Formatting failure silently drops the message.
- The `dm_errno_or_class` callback argument is currently unused.
