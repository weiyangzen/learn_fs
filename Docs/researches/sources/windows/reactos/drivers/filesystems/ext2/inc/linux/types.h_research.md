# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/types.h

This header maps Linux scalar types and annotations onto NT/ReactOS build types.

Key definitions:
- Includes `linux/config.h`, NT kernel/disk headers, Win32 definitions, and C runtime headers.
- Defines fixed-width Linux-style types: `__u8`, `__s8`, `__u16`, `__s16`, `__u32`, `__s32`, `__u64`, `__s64`.
- Defines short aliases `s8`/`u8` for ReactOS and `s16`/`u16`/`s32`/`u32`/`s64`/`u64` for MSVC or ReactOS.
- Maps `__le16`, `__le32`, and `__le64` to unsigned integer aliases; defines `__be16` and `__be32` as bitwise-marked types.
- Defines `bool` as `BOOLEAN`.
- Neutralizes compiler annotations/macros: `__attribute__`, `__bitwise`, `__releases`, `noinline`, `__acquire`, `__release`, `preempt_enable`, and `preempt_disable`.
- Defines Linux identity/FS types: `uid_t`, `gid_t`, `pid_t`, `gfp_t`, `umode_t`, `sector_t`, `blkcnt_t`, and `loff_t`.
- Defines `BITS_PER_LONG` as 32 and `ORDER_PER_LONG` as octal `05`; separately defines pointer-sized `long_ptr_t`/`ulong_ptr_t` and `CFS_BITS_PER_LONG`/`CFS_ORDER_PER_LONG`.
- Provides old-MSVC fallback `__FUNCTION__` and a `BUG()` macro that calls `DbgBreakPoint()`.

Research notes:
- This is foundational for compiling ported Linux ext/JBD code in the NT kernel environment.
- Endianness type annotations are mostly documentation here; the bitwise checking attributes are compiled away.
