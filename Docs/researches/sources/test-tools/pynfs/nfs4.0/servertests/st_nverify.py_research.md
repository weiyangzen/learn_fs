# sources/test-tools/pynfs/nfs4.0/servertests/st_nverify.py

Purpose: Tests NFSv4 `NVERIFY`, the inverse of `VERIFY`, across mandatory attributes, object type attributes, deliberately changed sizes, no-current-filehandle handling, write-only attributes, and unsupported attributes for every standard test-tree object type.

Important APIs/types/functions: Helper functions `_try_mand`, `_try_type`, `_try_changed_size`, `_try_write_only`, and `_try_unsupported` feed dictionaries into `op.nverify`. The module imports `env.attr_info`, `c.do_getattrdict`, `c.supportedAttrs`, and constants such as `FATTR4_TYPE`, `FATTR4_SIZE`, `NF4REG`, `NF4DIR`, `NF4LNK`, `NF4BLK`, `NF4CHR`, `NF4FIFO`, and `NF4SOCK`.

Control flow: Helper functions construct a base `use_obj(path)` compound, append `NVERIFY`, and often append another `use_obj(path)` to confirm compound continuation or short-circuit behavior. Repeated public tests pass each fixture path and expected object type into the shared helpers.

State and persistence behavior: Read-only except for observing current attributes. It computes supported and unsupported masks dynamically from the server.

Dependencies and integration points: Integrates tightly with environment attribute metadata (`mandatory`, `writeonly`, `sample`, `mask`) and client attribute encoders.

Risks: Server-specific attribute support affects which unsupported cases run. A misleading message in `_try_unsupported` says `VERIFY` in one branch, but the operation is `NVERIFY`.

Test signals: Expects matching attributes to produce `NFS4ERR_SAME`, changed size to succeed (`NFS4_OK`), write-only attributes to return `NFS4ERR_INVAL`, unsupported attributes to return `NFS4ERR_ATTRNOTSUPP` or `INVAL` for write-only unsupported attributes, and no filehandle to return `NFS4ERR_NOFILEHANDLE`.
