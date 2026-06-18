# File Research: sources/virtualization/nvme-cli/libnvme/src/libnvme.h.in

This template generates the public aggregate `libnvme.h`.

Content:
- C++ guards with `extern "C"`.
- Includes common libnvme headers for accessors, filters, ioctl, lib types, linux helpers, memory, commands, types, tree, and utilities.
- Contains `@FABRICS_INCLUDE@`, filled by Meson to include fabrics/NBFT/accessors-fabrics headers only when fabrics support is enabled.

Integration role:
- Produces installed top-level public libnvme header.
