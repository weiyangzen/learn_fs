# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-mi.c

## Role

Build-time fallback for NVMe-MI support when management interface support is disabled.

## Behavior

- `libnvme_mi_status_to_string()` returns `"MI support disabled"`.
- MI transport open/init and MI admin passthrough functions return `-ENOTSUP`.
- MI transport close is a no-op.

## Dependencies

Includes `errno.h`, `libnvme.h`, and `compiler-attributes.h`.

## Notes

This preserves public and internal transport symbols for builds without MI support. Callers get deterministic unsupported-feature results.
