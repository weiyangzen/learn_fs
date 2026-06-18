# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/ocfs2_internals.h

## Role

This header mirrors selected OCFS2 kernel-internal lock and LVB definitions for debug-only user-space inspection.

## Contents

It defines DLM lock modes, LVB length, OCFS2 lock flags, AST action values, unlock action values, LVB version constants, and two metadata LVB layouts used by older and newer OCFS2 versions.

## Usage

`dump_fs_locks.c` and `dump_dlm_locks.c` use these definitions to decode lock state and metadata lock value blocks.

## Risk Areas

The file intentionally duplicates kernel-internal definitions. If the kernel debugfs protocol or LVB layout changes, this copy can become stale.
