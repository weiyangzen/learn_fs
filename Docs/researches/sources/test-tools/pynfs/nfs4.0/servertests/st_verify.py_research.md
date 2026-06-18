# sources/test-tools/pynfs/nfs4.0/servertests/st_verify.py

Purpose: Tests NFSv4 `VERIFY` across mandatory attributes, object type attributes, deliberately incorrect sizes, no-current-filehandle handling, write-only attributes, and unsupported attributes for standard object types.

Important APIs/types/functions: Mirrors `st_nverify.py` with helpers `_try_mand`, `_try_type`, `_try_changed_size`, `_try_write_only`, and `_try_unsupported`, but calls `op.verify`. Uses `env.attr_info`, `c.do_getattrdict`, and `c.supportedAttrs`.

Control flow: Matching mandatory/type attributes are verified and followed by another path use to confirm compound continuation. Changed-size tests increment `FATTR4_SIZE` and expect `VERIFY` to fail with `NOT_SAME`. Attribute-class tests iterate environment metadata over all fixture object types.

State and persistence behavior: Read-only except for observing live attributes. Supported attribute masks are dynamically queried.

Dependencies and integration points: Integrates with NFSv4 attribute descriptors from the environment and operation constructors from `nfs_ops`.

Risks: Attribute availability and write-only handling differ between servers. Imports `get_invalid_clientid` and `makeStaleId` are unused, suggesting copy/paste from related stateid tests.

Test signals: Expects success for matching attributes, `NFS4ERR_NOT_SAME` for changed size, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL` for write-only attrs, and `NFS4ERR_ATTRNOTSUPP` or `INVAL` for unsupported write-only attrs.
