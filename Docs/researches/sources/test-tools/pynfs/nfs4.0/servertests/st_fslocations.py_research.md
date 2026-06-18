# sources/test-tools/pynfs/nfs4.0/servertests/st_fslocations.py

## Purpose
`st_fslocations.py` tests referral and `FATTR4_FS_LOCATIONS` behavior around `NFS4ERR_MOVED`. It verifies how GETFH, GETATTR, and READDIR behave for a path supplied by `--usespecial`, including restricted attributes and `FATTR4_RDATTR_ERROR` handling.

## Important APIs, Types, And Functions
- `testReference`, `testReference2`, and `testReference3` inspect referral behavior and `fs_locations` fetches.
- `testAttr1a`/`1b` expect MOVED when GETATTR/READDIR requests normal attrs without FS_LOCATIONS or RDATTR_ERROR.
- `testAttr2a`/`2b` add `RDATTR_ERROR`; READDIR should report MOVED per-entry while returning what it can.
- `testAttr3a`/`3b` request only restricted attrs and expect success.
- `testAttr4a`/`4b` request FS_LOCATIONS plus RDATTR_ERROR and validate returned attr counts.
- `testAttr5a`/`5b` request FS_LOCATIONS without RDATTR_ERROR and validate partial attrs.

## Control Flow
Tests build paths from `env.opts.usespecial`. GETFH/LOOKUP reference tests walk from root with `PUTROOTFH`, `GETFH`, `LOOKUP`, and `GETFH` until a MOVED status is expected. Attribute tests use `c.use_obj`, `c.getattr`, `op.readdir`, `c.do_getattrdict`, or `c.do_readdir` and inspect returned per-entry attr dictionaries.

## State And Persistence Behavior
No test-created persistent state is required. The tests depend on an existing special referral node in the server export configured outside the module.

## Dependencies And Integration Points
Imports include NFS constants, `nfs4lib.list2bitmap`, `check`, and `nfs_ops`. The module integrates with test runner options via `env.opts.usespecial` and with client helpers for GETATTR/READDIR decoding.

## Risks And Edge Cases
- Tests require `--usespecial` to point at a valid referral; without that environment they are not meaningful.
- Several attr-count expectations are hard-coded and can be sensitive to server-specific allowed attrs around referrals.
- Print messages indicate exploratory inspection rather than strict comparison of `fs_locations` contents.

## Test Signals
Signals include `NFS4ERR_MOVED`, successful restricted GETATTR/READDIR, per-entry `FATTR4_RDATTR_ERROR == NFS4ERR_MOVED`, and expected attr dictionary sizes when FS_LOCATIONS is present or absent.
