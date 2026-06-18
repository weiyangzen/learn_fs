# File Research: sources/os/linux/linux-stable/fs/nfsd/export.h

## Summary
Public NFSD export declarations and core export data structures.

## Contents
Defines NFSv4 fs location records, per-export security flavor arrays, export UUID sizing, per-export stats counters, `struct svc_export`, and `struct svc_expkey`. It also exposes export lifecycle, lookup, root filehandle, pseudoroot, and access-check helpers.

## Important Details
`svc_export` stores the client auth domain, export flags, fsid, path, anon credentials, optional UUID, NFSv4 fs locations, secinfo flavors, pNFS layout/device state, xprtsec modes, and stats. `svc_expkey` maps client/fsid type/fsid bytes to a path for filehandle-based export resolution.

## Risks
Consumers must use `exp_get()` / `exp_put()` rather than managing cache refs directly. `svc_expkey.ek_fsid` is sized for multiple fsid encodings and must be interpreted with `key_len()`.
