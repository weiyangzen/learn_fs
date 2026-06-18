# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modconf.c

## Purpose

Defines the `mod_ops` implementations used by illumos loadable modules. Despite the filename, this file is not the driver.conf parser; it is the install/remove/info dispatch layer for module linkage types.

## Main Entry Points

- `mod_install()`, `mod_remove()`, and `mod_info()` walk a module’s `modlinkage` array and call type-specific install/remove/info methods, with rollback/reinstall behavior on partial failure.
- `mod_modname()` returns the module name from the owning `modctl`.
- `mod_driverops`, `mod_fsops`, `mod_syscallops`, `mod_strmodops`, `mod_sockmodops`, `mod_schedops`, `mod_execops`, `mod_dacfops`, `mod_ippops`, `mod_pcbeops`, `mod_brandops`, and `mod_kiconvops` bind linkage classes to concrete operations.

## Subsystem Behavior

Driver modules are installed by validating module linkage, resolving major number, rejecting MT-unsafe non-nexus drivers, checking bus ops revision, populating `devopsp[major]`, and setting STREAMS implementation fields when needed. Removal refuses active/unload-disabled drivers and restores `mod_nodev_ops`.

Filesystem modules validate `vfsdef`, allocate or find `vfssw` slots, merge mount option prototypes, call filesystem init, and optionally initialize VOP stats. Removal checks `vsw_count` and `vfs_opsinuse()` before clearing the slot.

System call modules patch `sysent` and, when enabled, `sysent32`; removal requires loadable/non-`SE_NOUNLOAD` state and a try-write lock. Scheduling class, exec format, STREAMS, socket, DACF, IPP, brand, PCBE, and kiconv modules each register/unregister with their respective global subsystem tables.

## Dependencies

Key dependencies include `modctl` ownership lookup, `devnamesp`, `devopsp`, STREAMS `fmodsw`, `vfssw`, `sysent`, `execsw`, scheduling class state, DACF, IPP, BrandZ, kiconv, CPC/PCBE, and socket module registration.

## Correctness Notes

The file is mostly state-table mutation code. Locking discipline matters around `devnames` locks, `vfssw` read/write locks, syscall `sy_lock`, scheduler class locks, and exec locks. Several module classes intentionally refuse unload under debug/autounload controls or by design, especially PCBE modules.
