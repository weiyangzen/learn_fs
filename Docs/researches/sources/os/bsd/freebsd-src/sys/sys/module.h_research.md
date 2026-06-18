# File Research: sources/os/bsd/freebsd-src/sys/sys/module.h

Defines kernel module metadata, declaration macros, dependency/version records, PNP info export, module locking, and userland module stat calls.

Key content:
- Metadata types: dependency, module declaration, version, PNP info.
- Defines module event types: load, unload, shutdown, quiesce.
- `moduledata_t` stores module name, event handler, and private data.
- `modspecific_t` union lets modules report custom scalar data through `kldstat`.
- `struct mod_depend`, `struct mod_version`, `struct mod_metadata`, and `struct mod_pnp_match_info` describe embedded metadata.
- Kernel macros:
  - `MODULE_METADATA` emits metadata into `modmetadata_set`.
  - `MODULE_DEPEND` records versioned dependencies.
  - `DECLARE_MODULE`, `DECLARE_MODULE_TIED`, and `DECLARE_MODULE_WITH_MAXVER` register modules through SYSINIT and attach kernel-version dependency metadata.
  - `MODULE_VERSION` records module version.
  - `MODULE_PNP_INFO` exports parseable driver match tables.
- PNP descriptor grammar is documented for matching fields such as U8/V16/U32/string/EISA/table keys.
- Declares global module sx lock and lock macros.
- Kernel module APIs include register, lookup by name/id, quiesce, reference/release, unload, id/name/specific/file accessors.
- Userland ABI includes `struct module_stat` and calls `modnext`, `modfnext`, `modstat`, and `modfind`.

Research relevance:
- Central to loadable filesystem, storage, and driver modules.
- Works directly with `linker.h` and `linker_set.h`.
- `mount.h` uses module declarations for `VFS_SET`.

Cautions:
- `DECLARE_MODULE_TIED` enforces exact `__FreeBSD_version`; regular module max version rounds to branch end unless `KLD_TIED`.
- Module metadata is embedded via linker sets, so linker behavior is part of the ABI.
