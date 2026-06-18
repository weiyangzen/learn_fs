# File Research: sources/os/linux/linux/fs/cachefiles/xattr.c

## Purpose
Stores and validates CacheFiles coherency metadata in backing filesystem extended attributes for cache objects and volumes.

## Main Elements
- Object xattr format: `struct cachefiles_xattr` stores object size, zero point, object type, content state, and netfs auxiliary coherency data.
- Volume xattr format: `struct cachefiles_vol_xattr` stores a reserved field and volume coherency data.
- `cachefiles_set_object_xattr()`: writes object coherency metadata and marks locally written cookies as dirty.
- `cachefiles_check_auxdata()`: reads object xattr and validates type, auxiliary data, object size, and dirty state.
- `cachefiles_remove_object_xattr()`: removes an object xattr to mark a backing file stale.
- `cachefiles_prepare_to_write()`: writes a dirty marker before local write unless the object is still a tmpfile.
- `cachefiles_set_volume_xattr()` and `cachefiles_check_volume_xattr()`: write and validate volume coherency metadata.

## Dependencies And Integration
Uses VFS xattr operations under mount write access and CacheFiles credential context supplied by callers. Provides coherency checks for `namei.c`, object commit in `interface.c`, and volume setup in `volume.c`.

## Risk Notes
Xattr mismatches return `-ESTALE` and force object or volume replacement. Dirty object detection is noted as a TODO for conflict resolution. Non-memory xattr write/remove failures can mark the whole cache dead.
