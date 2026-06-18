# File Research: sources/virtualization/libblockdev/src/plugins/Makefile.am

## Role
Build rules for top-level libblockdev plugin shared libraries and selected plugin subdirectories.

## Subdirectories
- Starts with `SUBDIRS = .`.
- Adds `fs` when `WITH_FS` is enabled.
- Adds `nvme` when `WITH_NVME` is enabled.
- Always adds `lvm` and `smart` subdirectories.

## Plugin Libraries
Conditionally builds plugin shared libraries:
- `libbd_btrfs.la`;
- `libbd_crypto.la`;
- `libbd_dm.la`;
- `libbd_loop.la`;
- `libbd_mdraid.la`;
- `libbd_mpath.la`;
- `libbd_nvdimm.la`;
- `libbd_swap.la`;
- `libbd_part.la`;
- `libbd_s390.la`.

## Common Build Pattern
Most plugin targets:
- include GLib/GIO and plugin-specific dependency CFLAGS;
- link `../utils/libbd_utils.la`;
- use `-version-info 3:0:0`;
- enforce `--no-undefined`;
- export symbols matching `^bd_.*`;
- include generated headers through `-I${builddir}/../../include/`;
- build with `-Wall -Wextra -Werror`.

## Btrfs Target
When `WITH_BTRFS` is set:
- builds `libbd_btrfs.la`;
- uses GLib, GIO, and libbytesize flags/libs;
- compiles `btrfs.c`, `btrfs.h`, `check_deps.c`, and `check_deps.h`.

## Installed Headers
The file conditionally installs public plugin headers matching enabled plugins. It also installs `fs.h` when `WITH_FS` is enabled, even though FS plugin implementation lives in a subdirectory.

## Notable Detail
The S390 block has two consecutive `libbd_s390_la_CPPFLAGS = ...` assignments; the second assignment overwrites the first rather than appending, so the earlier `-I${srcdir}/../utils/` include path is not retained by this Makefile fragment.

## Filesystem/Storage Relevance
This file determines which storage-operation plugins are actually built and installed. For this group, it is the build rule that turns `btrfs.c` and shared dependency checking into a loadable `libbd_btrfs` plugin.
