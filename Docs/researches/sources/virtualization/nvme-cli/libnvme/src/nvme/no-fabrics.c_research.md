# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-fabrics.c

## Role

Build-time fallback implementation for selected fabrics helpers when fabrics support is disabled.

## Behavior

- `traddr_is_hostname()` always returns `false`.
- `libnvmf_default_config()` is a no-op.
- `libnvmf_read_sysfs_fabrics_attrs()` is a no-op.
- `libnvme_ctrl_find()` still provides limited controller lookup on non-Windows builds by iterating subsystem controllers and matching transport plus optional case-insensitive `traddr`.

## Dependencies

Includes `private.h`, which supplies libnvme internal types and helpers such as controller iteration and string comparison helpers.

## Notes

The fallback keeps basic controller lookup usable in non-Windows builds even without full fabrics support, but ignores most fabrics-specific parameters beyond transport and `traddr`.
