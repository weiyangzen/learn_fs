# File Research: sources/os/linux/linux-stable/fs/coda/coda_linux.c

## Purpose
Provides Linux-specific Coda helper conversions for FIDs, open flags, inode types, and attribute translation between Coda/Venus and VFS structures.

## Main Interfaces
- Debug/name helpers: `coda_f2s()`, `coda_iscontrol()`.
- Open flag conversion: `coda_flags_to_cflags()`.
- Attribute conversion: `coda_inode_type()`, `coda_vattr_to_iattr()`, `coda_iattr_to_vattr()`.

## Control Flow
`coda_flags_to_cflags()` maps Linux `O_ACCMODE`, `O_TRUNC`, `O_CREAT`, and `O_EXCL` into Coda open flags sent to Venus. `coda_vattr_to_iattr()` applies Coda attributes to a VFS inode when fields are not set to sentinel `-1`, including mode/type, uid/gid, nlink, size, block count, and timestamps. `coda_iattr_to_vattr()` initializes every Coda attribute field to an ignored sentinel, then fills only fields marked valid by Linux `ia_valid`.

## Integration Points
Used throughout Coda lookup/create/setattr/open code when crossing the kernel/Venus protocol boundary.

## Risks And Review Focus
- Attribute sentinel handling is central to avoiding unintended metadata changes.
- UID/GID conversion uses `init_user_ns`, so idmapped mount semantics are not represented here.
- `coda_f2s()` uses a static buffer and is suitable only for transient debug formatting.
