# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/Makefile

## Purpose

Builds the OCFS2 userspace DLM filesystem module components.

## Contents

- SPDX license: `GPL-2.0-only`
- Adds `ocfs2_dlmfs.o` when `CONFIG_OCFS2_FS` is enabled.
- Defines `ocfs2_dlmfs-objs` as:
  - `userdlm.o`
  - `dlmfs.o`

## Research Notes

This Makefile ties the VFS-facing dlmfs implementation and the user DLM lock protocol wrapper into one object. It is gated by the broader OCFS2 filesystem configuration rather than a separate dlmfs-specific config symbol in this file.
