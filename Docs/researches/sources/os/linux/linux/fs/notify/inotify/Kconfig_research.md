# File Research: sources/os/linux/linux/fs/notify/inotify/Kconfig

## Role

This Kconfig file defines `CONFIG_INOTIFY_USER`, the userspace inotify interface.

## Configuration

`INOTIFY_USER` is a boolean option labeled "Inotify support for userspace". It selects `FSNOTIFY` and defaults to enabled.

The help text describes inotify as a file and directory monitoring API using a single open descriptor whose events are readable and poll/select-able. It notes improvements over dnotify, including multiple file events, one-shot support, and unmount notification.

## Design Notes

The config entry makes inotify userspace support a direct fsnotify client and keeps it enabled by default for normal Linux builds.
