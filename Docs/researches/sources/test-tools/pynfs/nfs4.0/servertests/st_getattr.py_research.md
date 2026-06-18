# sources/test-tools/pynfs/nfs4.0/servertests/st_getattr.py

## Purpose
`st_getattr.py` tests NFSv4 `GETATTR` across file types and attributes. It verifies mandatory attribute support, no-current-filehandle handling, write-only attribute rejection, unknown and empty attr requests, supported-attrs correctness, large legal attr requests, FS_LOCATIONS support, many repeated GETATTR operations, and selected optional attributes.

## Important APIs, Types, And Functions
- `_try_mandatory(t, env, path)` requests all mandatory attrs except `rdattr_error` and fails if any are missing.
- `_try_write_only(env, path)` requests size plus each write-only attr and expects `NFS4ERR_INVAL`.
- `_try_unknown(t, c, path)` requests attr bit 1000 and expects OK with no attrs.
- `_try_empty(t, c, path)` requests an empty attr list and expects OK with empty attrs.
- `_try_supported(t, env, path)` validates `FATTR4_SUPPORTED_ATTRS` contains all mandatory attrs and no bits outside `env.attr_info`.
- `_try_long(env, path)` requests all non-write-only legal attrs.
- `testMand*`, `testWriteOnly*`, `testUnknownAttr*`, `testEmpty*`, `testSupported*`, `testLong*`, and optional attr tests form the entrypoint matrix.

## Control Flow
Each type matrix test delegates to a helper with an environment path. Helpers build `use_obj(path)` compounds plus `GETATTR` and inspect response `obj_attributes`. Optional attr tests request one attr and accept OK or `NFS4ERR_ATTRNOTSUPP`, converting unsupported attrs to support failures. `testLotsofGetattrsFile` appends ninety GETATTR ops in one compound and accepts OK or `NFS4ERR_RESOURCE`.

## State And Persistence Behavior
The module does not mutate server state except for possible access-time effects on the server. It reads attributes from the existing test tree.

## Dependencies And Integration Points
It imports NFS constants, `check`, attribute-name helpers from `nfs4lib`, and `nfs_ops`. It relies on `Environment.attr_info`, environment object paths, and `NFS4Client.supportedAttrs`/compound helpers.

## Risks And Edge Cases
- Server interpretation of write-only attrs may return `NFS4ERR_ATTRNOTSUPP` instead of `NFS4ERR_INVAL` in some optional tests; helper expectations are stricter for the matrix.
- `_try_supported` assumes `env.attr_info` fully describes protocol-supported attrs; newer/generated constants could make this check stale.
- Optional attr tests mostly check support presence, not returned value semantics.
- The mounted-on-fileid test is nested under a disabled method-like block and is not normal test discovery.

## Test Signals
Signals include mandatory attr presence, empty/unknown request behavior, write-only attr rejection, `FATTR4_SUPPORTED_ATTRS` bit correctness, compound resource handling, support or attr-not-supported status for optional attrs, and no-current-filehandle status.
