# File Research: sources/virtualization/libblockdev/src/utils/dev_utils.h

This public header declares device utility APIs.

Definitions:
- `BD_UTILS_DEV_UTILS_ERROR` maps to `bd_utils_dev_utils_error_quark()`.
- Defines `_C_LOCALE` for locale-neutral libc errors.
- `BDUtilsDevUtilsError` currently has one generic failure value.
- Declares `bd_utils_resolve_device()` and `bd_utils_get_device_symlinks()`.

Research relevance:
- Exposes `/dev` path resolution and udev devlink discovery to plugins and consumers.
