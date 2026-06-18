# sources/security-integrity/fsverity-utils/common/common_defs.h

Purpose: This shared header defines common types, macros, endian helpers, array/rounding utilities, compile annotations, and compatibility glue used by both the fsverity library and CLI.

Important APIs and types: It provides fixed-width aliases such as `u8`, `u16`, `u32`, `u64`, helpers like `ARRAY_SIZE`, `DIV_ROUND_UP`, `roundup`, `min`, `max`, `is_power_of_2`, `ilog2`, endian conversion wrappers, and assertion/warning-style macros.

Control flow and state: The file contains macro-time logic only. It persists no state, but influences generated code, layout validation, and portability behavior.

Dependencies and integration points: Included by `lib_private.h`, `fsverity.h`, command implementations, and UAPI wrappers. It bridges Linux conventions into userspace project code.

Risks and test signals: Macro errors can silently affect hash tree layout, descriptor encoding, and ioctl structure interpretation. Test signals include digest vector stability, compile success under multiple platforms, and static-analysis coverage for integer conversions.
