# File Research: sources/os/bsd/freebsd-src/sys/sys/linker_set.h

Defines FreeBSD linker set declaration, population, iteration, and counting macros.

Key content:
- `__MAKE_SET_QV` emits weak `__start_set_<set>` and `__stop_set_<set>` symbols and places a pointer to a target symbol in an ELF section named `set_<set>`.
- Public macros include `TEXT_SET`, `DATA_SET`, `DATA_WSET`, `BSS_SET`, `ABS_SET`, and `SET_ENTRY`.
- `SET_DECLARE`, `SET_BEGIN`, `SET_LIMIT`, `SET_FOREACH`, `SET_ITEM`, and `SET_COUNT` provide typed access to collected entries.
- Userspace AddressSanitizer redzones are avoided with `__nosanitizeaddress`; kernel builds use an empty `__NOASAN`.
- PowerPC64 ELFv1 has a special `__MAKE_SET_CONST` rule because function pointers point to descriptors.

Research relevance:
- Linker sets are the compile/link-time registry mechanism used throughout the kernel for module metadata, sysinit records, device methods, and other extensible registries.
- `module.h` uses `DATA_SET(modmetadata_set, ...)` to collect dependency/version/PNP/module declarations.
- Filesystem modules declared via `VFS_SET` ultimately rely on module metadata and linker set collection.

Cautions:
- Sets contain addresses of objects, so iterator variables must be pointer-to-pointer style.
- Section packing assumptions are important; sanitizer redzones can break those assumptions without the no-ASAN annotation.
