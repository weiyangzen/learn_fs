# File Research: sources/windows/winfsp/src/sys/shutdown.c

## Purpose

`shutdown.c` defines the WinFsp shutdown dispatch routine.

## Main Contents

- `FspShutdown` is registered as an `FSP_DRIVER_DISPATCH`.

## Behavior

`FspShutdown`:

- Enters the major-function dispatch macro.
- Explicitly marks `IrpSp` as unused.
- Always returns `STATUS_INVALID_DEVICE_REQUEST`.
- Emits an empty leave trace through the WinFsp dispatch macro.

## Integration

This is a minimal dispatch stub. It does not perform filesystem flush, volume teardown, or shutdown-specific cleanup.
