# File Research: sources/local-fs/dlm/dlm_sand/ondisk.h

## Purpose
Declares the `dlm_sand` on-disk serialization helpers and defines little-endian conversion macros for big- and little-endian hosts.

## Contents
- Includes `<endian.h>` and `<byteswap.h>`.
- Defines `le16_to_cpu`, `le32_to_cpu`, `le64_to_cpu`, `cpu_to_le16`, `cpu_to_le32`, and `cpu_to_le64`.
- Declares header, node, summary, and record copy-in/copy-out functions.

## Dependencies
- Requires struct definitions from `sand_internal.h` before use.

## Risks / Gaps
- No fallback for unknown `__BYTE_ORDER` values.
- Header depends on external struct declarations but does not include `sand_internal.h` itself, so include ordering matters.
