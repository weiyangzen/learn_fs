# File Research: sources/teaching/minix/minix/servers/vfs/vnode.h

## Purpose
Declares the global vnode table and vnode lock mode aliases.

## Main Structure
`struct vnode` stores:
- owning FS endpoint and optional mapped FS endpoint,
- inode numbers for original and mapped inode,
- mode, owner, group, size,
- VFS and FS reference counters,
- block-special-file endpoint/device information,
- containing device and special-device number,
- owning `struct vmnt`,
- per-vnode TLL lock.

## Lock Mapping
- `VNODE_NONE` maps to `TLL_NONE`.
- `VNODE_READ` maps to `TLL_READ`.
- `VNODE_OPCL` maps to `TLL_READSER`.
- `VNODE_WRITE` maps to `TLL_WRITE`.

## Risks and Notes
The distinction between `v_ref_count`, `v_fs_count`, and `v_mapfs_count` is central to avoiding excessive file-server calls while preserving reference accounting.
