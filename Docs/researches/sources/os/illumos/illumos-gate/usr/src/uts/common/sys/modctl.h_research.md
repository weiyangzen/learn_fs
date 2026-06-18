# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modctl.h

Purpose: Defines loadable module linkage structures, module control syscall commands, module metadata structures, kernel module loader state, and module loader/exported APIs.

Key structures:
- `mod_ops`: install/remove/info vector.
- Module linkage structs: driver, syscall, filesystem, CPU, crypto, misc, IPP, streams, scheduler, exec, DACF, PCBE, brand, socket module, kiconv.
- `modlinkage`: revision and NULL-terminated linkage array.
- `modconfig`/`modconfig32`: driver binding configuration.
- `modspecific_info`, `modinfo`, and 32-bit variants for `MODINFO`.
- Stub structures: `mod_stub_info`, `mod_modinfo`.
- `modctl_t`: persistent kernel module control record with ID, module image, linkage, names, state bits, reference count, dependencies, load count, DTrace probe count, text range, generation count.

Command surface:
- `MODLOAD`, `MODUNLOAD`, `MODINFO`, path/binding/name/device policy/minor permission/retire/hotplug operations, and event/devname/hotplug subcommands.
- `MOD_MAXPATH`, `MOD_DEFPATH`, module name/linkinfo length limits.
- `MI_INFO_*` flags and `MI_LOADED`/`MI_INSTALLED`.

Kernel APIs:
- Module load/unload/hold/release/lookup, system file parsing, driver major/name helpers, stubs install/uninstall/reset, symbol lookup, autounload state, DDI dynamic module open/sym/close.
- DDI/DKI-visible module entry points: `_init()`, `_fini()`, `_info()`, `mod_install()`, `mod_remove()`, `mod_info()`.

Important details:
- `MI_INFO_NOBASE` exists so 32-bit apps on 64-bit kernels can avoid `EOVERFLOW` from base addresses.
- `modctl_t` repeats module text range so `mod_containing_pc()` can operate without grabbing locks.
- `moddebug` bit flags expose detailed loader/autounloader behavior toggles.

Relevance to subset A: Important OS infrastructure. Filesystem modules use `modlfs`/`mod_fsops`; executable, driver, and device policy loading also affect VFS/device integration.
