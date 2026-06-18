# File Research: sources/teaching/minix/minix/servers/vfs/vmnt.h

## Purpose
Declares the global virtual mount table and mount flags.

## Main Structure
`struct vmnt` stores:
- file-server endpoint and TLL lock,
- communication throttling state,
- device, mount flags, and FS capability flags,
- mounted-on vnode and root vnode,
- label, mount path, device/source path, filesystem type,
- cached statvfs fields.

## Flags
- `VMNT_READONLY`
- `VMNT_CALLBACK`
- `VMNT_MOUNTING`
- `VMNT_FORCEROOTBSF`
- `VMNT_CANSTAT`

## Lock Mapping
- `VMNT_READ` maps to `TLL_READ`.
- `VMNT_WRITE` maps to `TLL_READSER`.
- `VMNT_EXCL` maps to `TLL_WRITE`.

## Risks and Notes
`VMNT_CANSTAT` is important for `getvfsstat`, which can enumerate mounts without locking when `ST_NOWAIT` is used.
