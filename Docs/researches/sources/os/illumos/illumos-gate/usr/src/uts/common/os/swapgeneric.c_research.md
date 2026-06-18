# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/swapgeneric.c

## Purpose

Configures early root filesystem/device boot plumbing for illumos. Despite the historical “root, swap and dump devices” file description, this source is primarily concerned with discovering the root filesystem type and physical boot path, preloading the driver/module stack needed before boot services disappear, initializing the root VFS, and mounting root.

## Main Responsibilities

- Register the module as `root and swap configuration`.
- Load and initialize the selected root filesystem module.
- Create and hold `rootvfs`, then call `VFS_MOUNTROOT(rootvfs, ROOT_INIT)`.
- Resolve root device paths into `dev_t` values through `ddi_pathname_to_dev_t()`.
- Prompt for filesystem/device names when `RB_ASKNAME` is active.
- Read boot properties for root filesystem type and boot path.
- Preload root-path drivers, parent nexus drivers, platform modules, force-loaded modules, NFS boot modules, iSCSI boot modules, and network plumbing.
- Detect special boot forms including ramdisk boot archives, NFS/netboot, iSCSI boot, IP-over-InfiniBand netboot, and USB hub boot paths.

## Key Entry Points

- `_init()`, `_fini()`, `_info()`
  Standard module linkage.

- `rootconf()`
  Final root setup. It initializes cluster boot root configuration, loads the root filesystem module, looks up the VFS switch entry, initializes `rootvfs`, calls `pm_init()`, optionally plumbs network/iSCSI support, mounts root through `VFS_MOUNTROOT()`, records `rootdev`, and logs the mounted root.

- `getrootdev()`
  Converts `rootfs.bo_name` to a device number and retries with an iSCSI physical disk path when needed.

- `getfsname()`
  Console prompt helper used when booting with `RB_ASKNAME`.

- `loadrootmodules()`
  Main early boot module loader. It gets the root filesystem type, loads implementation and platform drivers, resolves and loads root bootpath drivers, preserves DHCP boot properties, preloads `/etc/system` `FORCELOAD` modules, loads NFS/iSCSI boot dependencies, and calls cluster boot preload support.

- `getfstype()`
  Determines a root or swap filesystem type. It maps root `nfs` to `nfsdyn` and `nfs2` to `nfs`, and uses `vfs_getvfssw()` to obtain/load the filesystem switch entry.

- `getphysdev()`
  Determines root/swap physical device path. For swap it verifies `ddi_pathname_to_dev_t()` succeeds and refuses floppy swap devices.

- `load_boot_driver()`
  Resolves aliases to major driver names, performs `modloadonly("drv", ...)`, and on SPARC preloads modules listed in `ddi-forceload`.

- `load_bootpath_drivers()`
  Duplicates and normalizes a boot path, maps it to devinfo, handles x86 leaf-driver fallback, loads IP-over-IB and USB hub support where needed, and loads all parent drivers.

- `load_boot_platform_modules()`
  Loads platform modules or parent drivers for existing hardware nodes.

- `path_to_devinfo()`
  Uses PROM node lookup plus `ddi_walk_devs()` to map a physical path to an illumos devinfo node.

- `netboot_over_ib()` and `netboot_over_iscsi()`
  Detect network boot variants from boot path syntax/properties.

## Important State and Dependencies

- Uses global boot state such as `rootfs`, `rootvfs`, `rootdev`, `boothowto`, `bootops`, `netboot`, `obp_bootpath`, `root_is_ramdisk`, and iSCSI boot properties.
- Depends on VFS switch lookup, kernel module loading, PROM/boot property APIs, DDI/devinfo traversal, STREAMS plumbing, cluster boot hooks, NFS boot helper modules, and iSCSI boot path translation.
- DHCP boot metadata is copied from boot properties into `dhcack`, `dhcacklen`, and `netdev_path` for later userland adoption.

## Filesystem Relevance

This is directly filesystem-relevant boot code. It determines which filesystem implementation becomes root, ensures the required drivers and network/storage modules are resident before mountroot, initializes the root `vfs_t`, and invokes the root filesystem’s `VFS_MOUNTROOT()` operation. It is a critical bridge between firmware boot paths, device discovery, module loading, and the VFS layer.

## Notable Edge Cases

- Root `nfs` naming is rewritten for dynamic NFS version selection.
- `netboot` and iSCSI boot are treated as mutually exclusive in `rootconf()`.
- NFS boot preloads several STREAMS/RPC/MAC/NFS helper modules while boot services can still supply I/O.
- iSCSI boot preloads network, iSCSI, and disk drivers, then attaches the pseudo `iscsi` node during root configuration.
- x86 may lack a complete PROM stub for the leaf boot device, so the code falls back to parent path lookup plus explicit leaf driver load.
- USB boot through hubs force-loads `hubd` because PROM-compatible properties can otherwise bind hub nodes to the wrong driver.
