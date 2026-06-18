# sources/test-tools/pynfs/nfs4.0/servertests/st_setattr.py

Purpose: Large `SETATTR` conformance suite covering mode changes, size changes, mixed size/owner changes, stateid handling, no filehandle, read-only/unsupported attributes, malformed attribute XDR, invalid UTF-8 principals, invalid timestamps, max size, non-file size setting, change attribute updates, and empty owner/group principals.

Important APIs/types/functions: Helpers `_set_mode`, `_set_size`, `_set_mixed`, `_try_readonly`, `_try_unsupported`, and `check_res` centralize mutation and verification. Imports `bitmap2list`, `dict2fattr`, `nfstime4`, `settime4`, `nfs_ops`, and many `FATTR4_*` constants.

Control flow: Common helpers issue `use_obj(file) + SETATTR`, verify status, compare `attrsset` against requested attributes, then refetch attributes with `do_getattrdict`. Public tests create target objects of different types and call helpers or build malformed `fattr4` payloads.

State and persistence behavior: Mutates file modes, sizes, ownership metadata, time metadata, and change attributes. Several tests create special objects and truncate files.

Dependencies and integration points: Depends on dynamic server supported-attribute masks, environment attribute metadata, object creation support, and correct XDR packing/unpacking in `nfs4lib`.

Risks: Attribute support and permission policy vary widely by server and export. `testInodeLocking` is explicitly risky in comments because it historically exposed kernel inode-locking bugs. `check_res` references `get_bitnumattr_dict()` without importing it, which may be a latent bug if unexpected attrs are returned.

Test signals: Checks `NFS4_OK`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_OPENMODE`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_ATTRNOTSUPP`, `NFS4ERR_BADXDR`, `NFS4ERR_FBIG`, `NFS4ERR_ISDIR`, and `NFS4ERR_SYMLINK`, plus direct failures on attrset/getattr mismatch and unchanged change attributes.
