# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-private.h

## Purpose

Private header shared by the NVMe plugin implementation files.

## Contents

- Defines `ZERO_INIT` with a clang-specific empty initializer fallback.
- Defines `_C_LOCALE` as the C locale handle used for locale-stable error text.
- Declares internal error helpers:
  - `_nvme_status_to_error()`
  - `_nvme_fabrics_errno_to_gerror()`
- Declares internal info helpers:
  - `_open_dev()`
  - `_nvme_alloc()`

## Dependencies and Interactions

- Included by `nvme.c`, `nvme-info.c`, `nvme-op.c`, and `nvme-fabrics.c`.
- Keeps cross-file helpers internal with `G_GNUC_INTERNAL`.
