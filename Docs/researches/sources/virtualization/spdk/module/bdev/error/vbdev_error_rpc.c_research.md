# File Research: sources/virtualization/spdk/module/bdev/error/vbdev_error_rpc.c

## Purpose
Exposes JSON-RPC methods for creating, deleting, configuring, and resuming SPDK error-injection bdevs.

## Main Entry Points
- `bdev_error_create` decodes `base_name` and optional `uuid`, then calls `vbdev_error_create()`.
- `bdev_error_delete` decodes `name`, calls `vbdev_error_delete()`, and completes asynchronously.
- `bdev_error_inject_error` decodes the injection target and behavior, validates NVMe status parameters, builds `vbdev_error_inject_opts`, and calls `vbdev_error_inject_error()`.
- `bdev_error_resume_pending` resolves the named bdev and calls `vbdev_error_resume_pending()`.

## Internal Mechanics
The RPC layer relies on generated autogen context structs and decode helpers for error I/O type and error type strings. The default injection count is one. NVMe status code type/status code must be specified only for NVMe failure injection; non-NVMe injection rejects nonzero NVMe status fields.

## Dependencies
Uses SPDK JSON-RPC, string/error helpers, logging, `vbdev_error.h`, and `spdk_internal/rpc_autogen.h`.

## Risks and Notes
Resume uses `spdk_bdev_get_by_name()` and passes the resulting bdev pointer to the module; it does not open a descriptor. Error responses mix SPDK JSON-RPC internal errors for decode failures with errno-style module errors for operational failures.
