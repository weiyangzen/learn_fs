# File Research: sources/os/linux/linux-stable/fs/dlm/Makefile

## Purpose

Builds the DLM kernel module/object and selects its component source files.

## Main Responsibilities

- Adds `dlm.o` under `CONFIG_DLM`.
- Composes `dlm-y` from callback, config, directory, lock, lockspace, membership, memory, communications, plock, recovery, request queue, user, and utility modules.
- Adds `debug_fs.o` when `CONFIG_DLM_DEBUG` is enabled.

## Dependencies

- Controlled by `CONFIG_DLM` and optionally `CONFIG_DLM_DEBUG`.
- The listed object files collectively implement DLM lockspaces, wire communication, recovery, userspace API, and diagnostics.
