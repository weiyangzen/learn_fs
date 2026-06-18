# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/utils.c

## Purpose
`utils.c` contains PROXY_V3 translation helpers for NFSv3/NLM statuses and NFSv3 attributes. It maps backend protocol results into Ganesha FSAL statuses, validates representable attribute masks, converts fattr3/pre/post attributes to FSAL attrlists, and converts FSAL setattr data into NFSv3 `sattr3`.

## Important APIs, Types, And Functions
`nfsstat3_to_fsal()` and `nfsstat3_to_fsalstat()` translate NFSv3 status codes. `nlm4stat_to_fsal()` and `nlm4stat_to_fsalstat()` translate NLM v4 statuses. `attrmask_is_posix()` validates that requested output attributes are limited to POSIX plus `ATTR_RDATTR_ERR`. `attrmask_valid()` validates setattr masks, including mutually exclusive client/server atime and mtime forms. `update_attrs_change()` derives FSAL change from max(mtime, ctime). `fattr3_to_fsalattr()`, `pre_attrs_to_fsalattr()`, `post_attrs_to_fsalattr()`, and `fsalattr_to_sattr3()` perform attribute conversion.

## Control Flow
Status conversion uses explicit switch statements and returns `ERR_FSAL_INVAL` with the original protocol status as minor only for unknown statuses. Attribute output conversion first validates the request mask, then copies `fattr3` directly into the FSAL attrlist because this codebase typedefs `fattr3` compatibly, updates change, and marks POSIX supported/valid. Weak-cache pre attrs expose ctime, mtime, size, and derived change only when present. Setattr conversion zeroes all optional fields, validates the mask, and sets NFSv3 option discriminants for mode, uid, gid, size, atime, and mtime.

## State And Persistence
No persistent state is stored. All functions are pure conversions except for logging.

## Dependencies And Integration Points
The file depends on generated NFSv3/NLM protocol types, FSAL conversion helpers such as `fsal2unix_mode()`, attrmask macros, Ganesha time helpers, and `proxyv3_fsal_methods.h`. `main.c` uses these helpers for nearly every NFSv3 operation, and `nlm.c` uses NLM status mapping.

## Risks
`attrmask_is_posix()` logs `ATTRS_NFS3` while allowing `ATTRS_POSIX | ATTR_RDATTR_ERR`, so diagnostics can be confusing. Direct `*fsal_attrs_out = *attrs` depends on the local typedef/layout contract; if generated protocol types diverge, conversion becomes unsafe. `NFS3ERR_REMOTE` maps to `ERR_FSAL_NAMETOOLONG`, which is semantically weak. `NFS3ERR_JUKEBOX` maps to `ERR_FSAL_LOCKED`, which may affect retry behavior. `fsalattr_to_sattr3()` currently ignores rawdev device-number payload even when `ATTR_RAWDEV` is allowed for mknod.

## Test Signals
Use table-driven tests for every NFSv3 and NLM status mapping. Validate accepted and rejected attr masks, especially mixed `ATTR_ATIME`/`ATTR_ATIME_SERVER` and mixed mtime forms. Round-trip representative fattr3 values into FSAL attrs, verify change derivation, and test mknod rawdev conversion expectations against backend behavior.
