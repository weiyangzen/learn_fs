# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_conf.c

## Scope And Role

`vfs_conf.c` defines early Darwin/XNU VFS global filesystem configuration. It provides root filesystem globals, the initial built-in `vfstable` entries, filesystem type numbering state, and the boot-time vnode operation vector descriptor list used by VFS initialization.

This file does not implement mount or vnode operations itself. It wires compiled-in filesystem modules and vnode operation classes into the broader VFS registration machinery implemented elsewhere, especially `kpi_vfs.c`.

## Root Filesystem Globals

The file defines:

- `struct mount *rootfs`: root filesystem mount pointer.
- `struct vnode *rootvnode`: root vnode pointer.
- `struct vnode *imgsrc_rootvnodes[MAX_IMAGEBOOT_NESTING]` when `CONFIG_IMGSRC_ACCESS` is enabled, representing imageboot source/root nesting.
- `int (*mountroot)(void) = NULL`: global root-mount entry hook.

These are shared kernel VFS globals used during boot and root filesystem setup.

## Built-In Filesystem Table

`vfstbllist[]` is the static initial `struct vfstable` array. Entries are conditionally compiled based on kernel configuration flags.

Defined filesystem type numbers include:

- `FT_DEVFS = 19`
- `FT_SYNTHFS = 20`
- `FT_ROUTEFS = 21`
- `FT_NULLFS = 22`
- `FT_BINDFS = 23`
- `FT_MOCKFS = 0x6D6F636B`

`fstypenumstart` begins after `FT_BINDFS`, so dynamically registered filesystem type numbers start after the standard built-in range.

Conditional table entries include:

- `devfs`, optionally marked `MNT_MULTILABEL` when MAC Framework support is enabled, and always marked with generic args and 64-bit readiness.
- `nullfs`, marked `MNT_DONTBROWSE | MNT_RDONLY` and 64-bit ready.
- `bindfs`, also marked `MNT_DONTBROWSE | MNT_RDONLY` and 64-bit ready.
- `mockfs`, marked local and optionally given `mockfs_mountroot`; the comment indicates it should remain the last standard mountroot candidate when configured.
- `routefs`, marked local and 64-bit ready.

The array ends with two `<unassigned>` empty `vfstable` slots. `maxvfsslots`, `numused_vfsslots`, `numregistered_fses`, `maxvfstypenum`, and `vfsconf` expose table capacity and registration state.

## Vnode Operation Vector Descriptor List

`vfs_opv_descs[]` is the NULL-terminated boot-time descriptor list used to build vnode operation vectors. It always includes the dead vnode operations and conditionally includes descriptors for:

- FIFO/socket vnode ops;
- special device vnode ops;
- memory filesystem ops;
- devfs normal, spec, devfd, and fdesc ops;
- nullfs ops;
- bindfs ops;
- mockfs ops.

This list is the static vnode class inventory consumed during VFS initialization before filesystems are used.

## Dependencies And Integration

The file includes internal mount and vnode headers and imports `nfs_conf.h`, while declaring external `vfsops`, mountroot functions, and `vnodeopv_desc` structures implemented by the respective filesystem modules.

The table entries are consumed by VFS initialization and registration code, while dynamically loaded filesystems use the separate registration path. MACF affects devfs labeling flags. Build flags determine which filesystems and operation vectors exist in the kernel image.

## Research Notes

The complete 330-line source file was read. It is a compact configuration file whose main importance is establishing the initial VFS filesystem table and vnode operation descriptor set at boot.
