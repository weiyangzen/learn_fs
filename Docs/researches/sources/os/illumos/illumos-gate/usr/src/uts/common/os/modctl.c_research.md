# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modctl.c

## Purpose

Implements the `modctl(2)` system call and the kernel module loading/unloading framework. It owns global module records, module setup at boot, dynamic loading through `kobj`, installation via `_init`, removal via `_fini`, dependency tracking, autounload, driver major bindings, minor permissions, device policy helpers, device retirement, devfs helpers, and DDI module-open APIs.

## Main Entry Points

- `mod_setup()` initializes major/syscall bindings, `devopsp`, `devnamesp`, module hash support, DACF, IPP, syscall locks, exec locks, classes, and autounload thread-specific state.
- `modctl()` dispatches privileged user commands such as `MODLOAD`, `MODUNLOAD`, `MODINFO`, driver alias binding, driver.conf load/unload, device path/devid queries, sysevents, minor permissions, devfs queries, device retirement, hotplug, and devname operations.
- `modload()`, `modload_qualified()`, `modloadonly()`, `modunload()`, `mod_remove_by_name()`, `modreap()`, and `mod_uninstall_daemon()` provide kernel module lifecycle APIs.
- `mod_hold_stub()` / `mod_release_stub()` support loadable stubs.
- `ddi_modopen()`, `ddi_modsym()`, and `ddi_modclose()` implement dynamic module/library reference loading for DDI clients.

## Module Lifecycle

Module records are `struct modctl` entries linked on the global `modules` list. `mod_hold_by_name_common()`, `mod_hold_by_id()`, and `mod_hold_by_modctl()` serialize access with `mod_lock`, `mod_busy`, `mod_want`, and `mod_cv`. Circular dependency detection uses `mod_inprogress_thread` and `mod_requisite_loading`.

`mod_load()` checks exclusion policy, loads object code through `kobj_load_module()` in a helper thread when possible, records linkage via `_info`, installs stubs, runs hotinlines, and notifies DTrace. `modinstall()` installs requisites then invokes `_init`. `moduninstall()` refuses primary/referenced/enabled modules, detaches drivers before `_fini`, then clears installed stubs on success. `mod_unload()` resets stubs, unloads kobj memory, releases requisites, and notifies DTrace.

## Device and Filesystem-Relevant Control

This file manages driver major aliases and binding state through `modctl_update_driver_aliases()`, `modctl_rem_major()`, `modctl_load_drvconf()`, and `modctl_unload_drvconf()`. It integrates with device tree binding/unbinding, driver.conf reloads, devfs cache invalidation, `/devices` attribute cleanup, `/dev` non-reconfiguring queries, device retirement persistence, devid-to-path lookup, minor-name/path lookup, framebuffer path query, and hotplug operations.

Minor permissions are loaded from nvlist payloads and stored per driver in `devnamesp[major]`. `dev_minorperm()` resolves defaults using exact/pattern matching, wildcard entries, clone-driver special handling, and alias fallback.

## Dependencies

Major dependencies include `kobj`, DDI/NDI, devfs/sdev, devpolicy, sysevents, DACF, IPP, DTrace callbacks, module stubs, instance database, binding-file hash tables, `devnamesp`, `devopsp`, syscall tables, exec tables, class setup, and power-management lock borrowing during module load.

## Correctness Notes

The highest-risk areas are lifecycle races and lock ordering. The code carefully avoids holding `mod_lock` across blocking operations, releases module holds before driver detach to avoid devinfo/module deadlocks, uses autounload disable counters to serialize cleanup windows, and preserves dependency reference counts through requisite lists. User-facing commands rely heavily on careful `copyin`/`copyout`, native vs 32-bit model conversion, length validation, and double-NUL path-list sizing.
