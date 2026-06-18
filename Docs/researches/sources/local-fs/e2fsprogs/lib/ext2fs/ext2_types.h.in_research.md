# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_types.h.in

## Purpose
Autoconf template for fixed-width ext2fs integer and endian-annotated types.

## Content Summary
The template:
- Avoids redefining types if Linux, blkid, or ext2 types are already present.
- Substitutes `@ASM_TYPES_HEADER@`.
- Defines `__u8`, `__s8`, `__u16`, `__s16`, `__u32`, `__s32`, `__u64`, and `__s64` from configure-provided typedefs or size probes.
- Emits intentional configure-time compile failures if a required width cannot be found.
- Undefines intermediate typedef macros.
- Includes `<stdint.h>`.
- Defines sparse/checker-compatible `__bitwise` and `__force`.
- Defines endian-tagged aliases `__le16`, `__le32`, `__le64`, `__be16`, `__be32`, `__be64`.
- Substitutes `@PUBLIC_CONFIG_HEADER@`.

## Integration
Generated into `ext2_types.h`, included by the public ext2fs headers before disk-format structs are defined.

## Risks and Notes
- Generated output is platform-specific.
- Type width correctness is foundational; all on-disk structs assume these widths.
- The endian aliases are mostly compile-time annotations but matter for sparse-style checking.
