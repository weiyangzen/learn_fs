# File Research: sources/os/linux/linux/fs/nfsd/export.h

Read completely: 142 lines.

Public NFSD export data model and function declarations shared by export lookup, filehandle verification, request processing, and procfs reporting.

Key responsibilities:
- Defines NFSv4 fs_locations structures and the `MAX_FS_LOCATIONS` limit.
- Defines secinfo flavor storage, `MAX_SECINFO_LIST`, and `EX_UUID_LEN`.
- Defines per-export stats counters for stale filehandles, read bytes, and write bytes.
- Defines `struct svc_export`, carrying cache state, auth domain, export flags/fsid/path, anon credentials, UUID, fs_locations, secinfo flavor list, pNFS layout/device data, xprtsec modes, stats, and deferred RCU work.
- Defines `struct svc_expkey`, mapping client plus fsid key to an export path.
- Provides convenience predicates for sync/nohide/write-gather options and inline cache ref helpers `exp_put` and `exp_get`.
- Declares export lifecycle, lookup, pseudoroot, root filehandle, and access-check APIs.

Dependencies:
- Pulls in sunrpc cache, percpu counters, workqueues, UAPI export flags, and NFSv4 types.

Notable risks:
- `struct svc_export` is the shared contract for many nfsd subsystems; ownership of pointer fields such as `ex_uuid`, `ex_fslocs.locations`, `ex_devid_map`, and `ex_stats` is transferred during cache updates.
- `svc_expkey.ek_fsid` stores multiple fsid formats in a fixed six-word array, so callers must use `key_len()` consistently.
