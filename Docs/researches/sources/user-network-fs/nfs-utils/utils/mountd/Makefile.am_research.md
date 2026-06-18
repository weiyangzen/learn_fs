<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/mountd/Makefile.am

## Purpose

`mountd/Makefile.am` defines the automake build and install behavior for the `rpc.mountd` service.

## Important APIs, types, and functions

It builds `mountd` from `mountd.c`, `mount_dispatch.c`, `rmtab.c`, `svc_run.c`, and `mountd.h`. It links export, NFS, misc, reexport, optional junction, BSD, tcp-wrappers, NSL, blkid, uuid, tirpc, pthread, and netlink libraries. Install hooks rename the binary to include `rpc.` and optional kernel prefix and create `rpc.mountd.8` manpage links.

## Control flow

Automake processes the file into build rules. Conditional `CONFIG_JUNCTION` adds junction support. Custom install/uninstall hooks rename executables and manage manpage symlinks after standard automake targets.

## State and persistence behavior

No runtime state is managed. Installation mutates files under `sbindir` and `man8dir`.

## Dependencies and integration points

The target includes support/export headers and links to the same support libraries that implement export authentication, cache upcalls, and reexport behavior consumed by `mountd.c`.

## Risks and edge cases

The rename hooks assume installed program names and manpage suffix transformations match automake behavior. Packaging systems that use staged installs must preserve `DESTDIR` behavior. Optional library ordering matters for systems with static or strict linkers.

## Test signals

Build tests should cover junction enabled/disabled, install and uninstall into a `DESTDIR`, prefixed binary names, manpage symlink creation, and link success with/without tcp-wrapper and netlink libraries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/Makefile.am -->
