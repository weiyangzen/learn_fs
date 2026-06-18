# File Research: sources/local-fs/apfs-fuse/ApfsLib/Endian.h

This header provides endian conversion support and disk-field wrapper types for APFS parsing. It currently forces `APFS_LITTLE_ENDIAN` and undefines `APFS_BIG_ENDIAN`, then supplies platform-specific byte-swap definitions for MSVC, Linux, and macOS.

On little-endian builds, little-endian disk types are simple typedefs to native integer types, while big-endian integer fields are packed wrapper structs with assignment and conversion operators that byte-swap on access. This matches APFS’s little-endian disk layout while still allowing some big-endian fields for formats such as GPT.

The big-endian build path defines little-endian wrapper structs and native big-endian typedefs, but it is effectively dormant because the file unconditionally defines `APFS_LITTLE_ENDIAN`. The comment says this should later be configuration-driven. The big-endian branch also appears less complete than the little-endian branch, so actual cross-endian support should be treated as aspirational unless tested.

The header also includes a disabled generic `be<T>`/`le<T>` template approach under `#if 0`, suggesting the current code chose explicit typedefs/wrappers to keep disk structs simple and packed. MSVC handling temporarily defines `__attribute__` away to let packed wrappers compile.
