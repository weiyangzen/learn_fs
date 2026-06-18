# File Research: sources/virtualization/nvme-cli/common.h

- Purpose: shared portability and MMIO helper header.
- General helpers: defines `ARRAY_SIZE`, simple `min/max`, `__packed`, and Windows wrappers for `mkdir`, `fsync`, and `getpagesize`.
- Endian dependency: includes CCAN endian helpers and uses `leint32_t/leint64_t`.
- MMIO behavior: provides raw read/write helpers; on AArch64 uses inline assembly `ldr/str` with `Qo` constraints to avoid MMIO instructions that hypervisors may not decode.
- Register access: `mmio_read64` reads two 32-bit little-endian halves because some devices fail 64-bit MMIO; `mmio_write64` can either write two 32-bit halves or one 64-bit little-endian value depending on `write32`.
