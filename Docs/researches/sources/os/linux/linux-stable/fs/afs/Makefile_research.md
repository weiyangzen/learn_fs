# File Research: sources/os/linux/linux-stable/fs/afs/Makefile

This Makefile builds the AFS client module/object.

Major contents:
- Defines `kafs-y` as the object list for the AFS client.
- Includes address management, cell/server/volume management, callback service, directory operations, file operations, locking, RxRPC client helpers, security, validation, VL service, YFS protocol, writeback, xattrs, mountpoints, and dynroot support.
- Adds `proc.o` conditionally when `CONFIG_PROC_FS` is enabled.
- Hooks the composite object into `obj-$(CONFIG_AFS_FS)` as `kafs.o`.

Relevance to this batch:
- The listed files here are a subset of the full `kafs-y` object.
- `addr_list.o`, `addr_prefs.o`, `callback.o`, `cell.o`, `cm_security.o`, `cmservice.o`, `dir.o`, and `dir_edit.o` are directly included.
- The current files depend on other objects such as `fsclient.o`, `vlclient.o`, `rotate.o`, `server.o`, `volume.o`, `validation.o`, `security.o`, and `internal.h` declarations.
