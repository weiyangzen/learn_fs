# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-op.c

## Purpose

Implements active NVMe management operations: device self-test, low-level format, and sanitize.

## Main Responsibilities

- Map libblockdev self-test actions to NVMe Device Self-test command codes.
- Select a supported LBA format by requested data and metadata size.
- Run Format NVM with guardrails for namespace-versus-controller scope.
- Refresh kernel block state after format.
- Submit Sanitize commands with selected action and overwrite options.

## Important Functions

- `bd_nvme_device_self_test()` opens a controller or namespace device, resolves NSID when possible, and issues `nvme_dev_self_test()`.
- `find_lbaf_for_size()` identifies the current or requested LBA format index from Identify Namespace data.
- `bd_nvme_format()` validates formatting scope, maps secure erase options, calls `nvme_format_nvm()`, and updates kernel namespace/block state.
- `bd_nvme_sanitize()` maps sanitize action values and calls `nvme_sanitize_nvm()`.

## Dependencies and Interactions

- Uses `_open_dev()` and `_nvme_alloc()` from `nvme-info.c`.
- Uses `_nvme_status_to_error()` from `nvme-error.c`.
- Uses Linux ioctls `NVME_IOCTL_RESCAN`, `BLKBSZSET`, and `BLKRRPART` after format.
- Uses libnvme command argument structs: `nvme_dev_self_test_args`, `nvme_format_nvm_args`, and `nvme_sanitize_nvm_args`.

## Notable Details

- Controller character devices are detected when `nvme_get_nsid()` fails with `ENOTTY`; then NSID is set to all namespaces.
- Formatting a namespace is rejected with `BD_NVME_ERROR_WOULD_FORMAT_ALL_NS` when controller FNA says namespace format would affect all namespaces.
- When called on a controller device, `find_lbaf_for_size()` uses namespace ID 1 as the reference namespace.
- After namespace format with a changed LBA size, the code updates the block size and rereads the partition table.
- Sanitize returns immediately after command submission; progress is obtained through `bd_nvme_get_sanitize_log()`.
