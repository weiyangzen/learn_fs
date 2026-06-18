# File Research: sources/virtualization/spdk/module/bdev/error/vbdev_error.h

## Purpose
Declares the private/public interface for the error-injection bdev module.

## Main Contents
- `spdk_delete_error_complete`, the async delete callback type.
- `vbdev_error_create()` and `vbdev_error_delete()` for lifecycle management.
- `struct vbdev_error_inject_opts`, carrying I/O type, error type, NVMe status fields, injection count, queue-depth threshold, and corruption settings.
- `vbdev_error_inject_error()` for configuring injection behavior.
- `vbdev_error_resume_pending()` for releasing I/O held by pending injection.

## Dependencies
Includes SPDK standard headers, bdev API, public error module definitions, and UUID definitions.

## Risks and Notes
The header exposes raw numeric fields matching RPC-generated decode values, so validation is mostly in callers and the implementation. `vbdev_error_inject_error()` takes a mutable `char *name` even though it treats the name as read-only.
