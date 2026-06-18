# sources/test-tools/pynfs/nfs4.0/servertests/st_access.py

## Purpose
`st_access.py` tests the NFSv4 `ACCESS` operation across regular files, directories, symlinks, FIFOs, sockets, character devices, and block devices. It verifies readable access, all valid access-bit combinations, invalid access masks, and no-current-filehandle handling.

## Important APIs, Types, And Functions
- `_valid_access_ops` contains every subset of the six defined access bits.
- `_invalid_access_ops` contains masks with bits beyond the legal `0x3f` range.
- `_try_all_combos(t, c, path, forbid=0)` sends ACCESS for all valid masks and verifies returned `supported` and `access` are subsets of the requested mask and exclude type-meaningless bits.
- `_try_read(c, path)` checks that `ACCESS4_READ` succeeds.
- `_try_invalid(t, c, path)` accepts either `NFS4ERR_INVAL` or an OK response whose returned bitmasks do not expose invalid bits.
- `testRead*`, `testAll*`, `testNoFh`, and `testInvalids*` are per-object-type test entry points with FLAGS/DEPEND/CODE metadata.

## Control Flow
Each test builds a compound from `c.use_obj(path)` plus `op.access(mask)`, runs it through `NFS4Client.compound`, and calls `check`. Valid-combination tests inspect the last response's `supported` and `access` fields. Invalid tests loop over invalid masks and either require `NFS4ERR_INVAL` or validate that an OK server did not echo illegal bits.

## State And Persistence Behavior
The module does not create persistent state. It uses the prebuilt environment test tree and reads protocol access masks from server responses.

## Dependencies And Integration Points
It imports NFSv4 constants, `check`, and `nfs_ops.NFS4ops`. It depends on environment paths such as `opts.usefile`, `opts.usedir`, `opts.uselink`, and special object paths created by `Environment._maketree`.

## Risks And Edge Cases
- The `forbid` masks encode test expectations about meaningful bits per type; server implementations with different but spec-legal support semantics may get warnings/failures.
- `_try_invalid` allows OK for invalid input if returned masks are sanitized, reflecting interoperability flexibility.
- The tests assume the special object paths exist; missing device/socket support in the test export can invalidate dependent cases.

## Test Signals
Primary signals are ACCESS status, subset relations between requested/supported/access masks, rejection or sanitization of invalid bits, and `NFS4ERR_NOFILEHANDLE` when ACCESS is sent without a current filehandle.
