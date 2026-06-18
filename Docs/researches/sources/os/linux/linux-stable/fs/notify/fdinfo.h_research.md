# File Research: sources/os/linux/linux-stable/fs/notify/fdinfo.h

## Summary
Small header declaring fdinfo display hooks for inotify and fanotify.

## Contents
Declares `inotify_show_fdinfo()` and `fanotify_show_fdinfo()` under `CONFIG_PROC_FS` and the corresponding feature configs. When procfs is disabled, both names are defined as `NULL`.

## Risks
The header is intentionally minimal. Callers use these symbols in file operations, so the config-dependent `NULL` fallback must remain compatible with file operation initialization.
