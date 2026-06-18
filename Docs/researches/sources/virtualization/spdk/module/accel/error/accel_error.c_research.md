# File Research: sources/virtualization/spdk/module/accel/error/accel_error.c

## Purpose

Implements a low-priority SPDK accel module that wraps the software accel module and injects configured errors for testing.

## Main Responsibilities

- Registers accel module `"error"` with priority `INT_MIN`.
- Wraps the software accel module's IO channel and submit path.
- Supports per-channel error injection settings copied from global config.
- Can corrupt task output or complete tasks with injected failure.
- Provides config JSON output for active injection rules.
- Currently supports injection for CRC32C operations.

## Injection Types

From header/API:
- `disable`
- `corrupt`
- `failure`

## Key Control Flow

- `accel_error_module_init()` obtains the `"software"` accel module, records its context size, and registers a wrapper IO device.
- `accel_error_submit_tasks()` checks whether to inject for the task opcode and interval/count settings.
- Corruption injection wraps the completion callback or sequence step callback, then forwards to software.
- Failure injection queues a synthetic completion handled by `accel_error_poller`.
- `accel_error_inject_error()` validates opcode support, updates global settings, and applies them to all existing channels with `spdk_for_each_channel`.

## Notes / Risks

- Only `SPDK_ACCEL_OPC_CRC32C` is supported by `accel_error_supports_opcode`.
- CRC corruption simply increments `*task->crc_dst`.
- The module depends on the software accel module being present.
