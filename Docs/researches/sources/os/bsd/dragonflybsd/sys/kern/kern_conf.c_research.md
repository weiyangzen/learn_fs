# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_conf.c

## Purpose

Implements DragonFlyBSD character-device identity, creation, destruction, aliasing, autocloning, reference, and name helper APIs. This file is the compatibility-facing layer above `devfs` and `dev_ops`, while lower-level operation dispatch lives in `kern_device.c`.

## Key Responsibilities

- Converts between `cdev_t`, old-style `dev_t`, user major/minor encodings, and display names.
- Creates device nodes through `make_dev*()` and `devfs_create_dev()`.
- Creates internal-only or devfs-only device objects with the `make_only_*()` family.
- Destroys devices and aliases through `devfs_destroy_dev()` / alias helpers.
- Supports autocloning device entries using devfs clone handlers.
- Wraps device lifetime around `sysref` via `reference_dev()` and `release_dev()`.

## Main Entry Points

- `major()`, `minor()`, `lminor()` return device major/minor values from `cdev_t`; `major()` deliberately reads `si_umajor` instead of `si_ops` because destroyed devices may have their ops replaced with `dead_dev_ops`.
- `devid_from_dev()` and `dev_from_devid()` bridge `cdev_t` and devfs inode/device IDs.
- `uminor()`, `umajor()`, `makeudev()` preserve old userland device-number packing.
- `makedev_unit_b32()` formats a unit suffix in base 32.
- `make_dev()`, `make_dev_covering()`, `make_only_devfs_dev()`, `make_only_dev()`, `make_only_dev_covering()` allocate/initialize `cdev_t` instances and optionally create devfs-visible nodes.
- `destroy_dev()`, `destroy_only_dev()`, `sync_devs()` clean up devices and drain disk/devfs configuration work.
- `make_dev_alias()` / `destroy_dev_alias()` create/remove devfs aliases.
- `make_autoclone_dev()` / `destroy_autoclone_dev()` manage clone-handler-backed device names.
- `reference_dev()` / `release_dev()` operate on `dev->si_sysref`.
- `devtoname()` lazily synthesizes `#driver/minor` names when `si_name` is empty or internal.

## Important Implementation Details

- `compile_dev_ops()` is called before device creation, ensuring missing device operation slots are populated from defaults.
- `make_dev()` returns an ad-hoc, unreferenced device pointer; callers storing it long-term must call `reference_dev()`.
- `destroy_dev()` assumes the caller owns a real reference; the comments warn against `destroy_dev(make_dev(...))`.
- `destroy_only_dev()` releases three references, reflecting the specific reference arrangement created by `make_only_dev()`/devfs internals.
- `make_autoclone_dev()` installs a clone handler and creates a covering device using `default_dev_ops` over the real backing ops.
- `sync_devs()` calls `disk_config()` and `devfs_config()` twice to flush asynchronous disk/devfs operations before mountroot or module unload.

## Dependencies and Coupling

- Strongly coupled to `devfs` APIs: `devfs_new_cdev`, `devfs_create_dev`, `devfs_destroy_dev`, `devfs_make_alias`, `devfs_clone_handler_add`, clone bitmap helpers.
- Depends on `struct dev_ops`, `dead_dev_ops`, and `default_dev_ops` from the device-operation layer.
- Used by driver attach/detach paths, disk code, clone devices, and `/dev` namespace management.

## Filesystem/Storage Relevance

This file is central to exposing kernel devices as `/dev` nodes. Filesystems and block layers reach storage through device vnodes, so correct lifetime and devfs naming here directly affect mountable disks, pseudo devices, and driver teardown safety.

## Research Notes

- The API distinguishes ad-hoc returned pointers from caller-owned references; misuse can create lifetime bugs.
- Major/minor compatibility helpers preserve legacy encodings and can return `NOUDEV` when values cannot be represented.
- Autoclone setup bridges devfs name lookup and runtime device instance creation.
