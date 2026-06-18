# File Research: sources/virtualization/libblockdev/src/lib/blockdev.h

## Role
Public core header for initializing and querying the libblockdev library.

## API
- Includes `blockdev/utils.h`, GLib, and `plugins.h`.
- Defines the `BD_INIT_ERROR` quark and `BDInitError` values:
  - `BD_INIT_ERROR_FAILED`;
  - `BD_INIT_ERROR_PLUGINS_FAILED`;
  - `BD_INIT_ERROR_NOT_IMPLEMENTED`.
- Declares:
  - `bd_init`;
  - `bd_ensure_init`;
  - `bd_reinit`;
  - `bd_try_init`;
  - `bd_try_reinit`;
  - `bd_is_initialized`.

## Dependencies and Interactions
- Uses `BDPluginSpec` from `plugins.h`.
- Uses `BDUtilsLogFunc` from `blockdev/utils.h`.
- The declarations correspond directly to implementations in `blockdev.c.in`.

## Filesystem/Storage Relevance
This is the public entry point clients must use before invoking plugin APIs for filesystem, block, crypto, RAID, NVMe, or related storage operations.
