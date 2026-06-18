# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsfh.c

## Summary
Implements NFSD filehandle verification, composition, update, release, and attribute capture. It translates on-the-wire filehandle bytes into exports/dentries and enforces export security before VFS operations proceed.

## Main APIs
- `fh_verify()` and `fh_verify_local()`.
- `fh_compose()` and `fh_update()`.
- `fh_getattr()`, `fh_fill_pre_attrs()`, `fh_fill_post_attrs()`, `fh_fill_both_attrs()`.
- `fh_put()`, `SVCFH_fmt()`, `fsid_source()`, `nfsd4_change_attribute()`.

## Behavior
Verification decodes the fsid portion, finds the matching export, optionally verifies a SipHash MAC on signed filehandles, decodes the fileid via `exportfs_decode_fh_raw()`, checks pseudoroot rules, sets export credentials, checks secure-port/xprtsec/security-flavor policy, and finally checks NFSD permissions. Composition chooses an fsid encoding from the reference handle, export fsid, UUID, or device identity, then encodes the filesystem-specific fileid and optional MAC.

## State and Synchronization
Each `svc_fh` owns dentry/export references until `fh_put()`. Write operations use `fh_want_write()`/`fh_drop_write()` mount write protection. Weak cache consistency data is captured in the filehandle around mutating operations. NFSv4 change attributes combine change cookies with ctime for non-monotonic regular-file counters.

## Risks
Filehandle correctness depends on matching fsid type, export policy, subtree-check acceptability, and optional MAC handling. `fh_verify()` can be called repeatedly on one handle with different access modes, so callers must still call `fh_put()` exactly once when done. Signed filehandles become stale if `fh_key` is absent or changed unexpectedly.
