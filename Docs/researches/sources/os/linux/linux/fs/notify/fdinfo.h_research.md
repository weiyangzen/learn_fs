# File Research: sources/os/linux/linux/fs/notify/fdinfo.h

## Role

This small header declares fsnotify fdinfo hooks for inotify and fanotify.

When `CONFIG_PROC_FS` is enabled, it exposes `inotify_show_fdinfo()` and/or `fanotify_show_fdinfo()` according to subsystem config. Without procfs, both names are defined as `NULL`.

## Design Notes

The header lets file-operation tables assign `.show_fdinfo` unconditionally inside subsystem code while compiling away procfs support cleanly.
