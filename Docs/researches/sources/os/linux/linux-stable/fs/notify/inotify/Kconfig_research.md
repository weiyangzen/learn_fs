# File Research: sources/os/linux/linux-stable/fs/notify/inotify/Kconfig

## Summary
Kconfig entry for userspace inotify support.

## Contents
Defines `INOTIFY_USER` as a default-enabled bool, selects `FSNOTIFY`, and describes inotify fd-based file and directory event monitoring with poll/select support, one-shot watches, and unmount notifications.

## Risks
Disabling this removes the userspace inotify syscalls and associated support objects while the lower fsnotify infrastructure can still be selected by other clients.
