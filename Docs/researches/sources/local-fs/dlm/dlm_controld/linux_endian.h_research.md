# File Research: sources/local-fs/dlm/dlm_controld/linux_endian.h

This header provides Linux-style endian conversion macros in userspace using glibc `<endian.h>` and `<byteswap.h>`.

Key behavior:
- On big-endian systems, big-endian conversions are identity and little-endian conversions byte-swap.
- On little-endian systems, little-endian conversions are identity and big-endian conversions byte-swap.
- It defines `be16_to_cpu`, `be32_to_cpu`, `be64_to_cpu`, `cpu_to_be16`, `cpu_to_be32`, `cpu_to_be64`, `le16_to_cpu`, `le32_to_cpu`, `le64_to_cpu`, `cpu_to_le16`, `cpu_to_le32`, and `cpu_to_le64`.
- It includes an Alpha-specific replacement for `bswap_64`.

Used by:
- `plock.c` for marshaling `struct dlm_plock_info`, plock checkpoint data, and resource metadata into little-endian wire/storage format.
