# File Research: sources/os/linux/linux/fs/nfsd/nfsproc.c

## Summary
Implements NFSv2 server procedure handlers and the NFSv2 SunRPC procedure table. It bridges decoded NFSv2 RPC arguments to common NFSD VFS helpers and maps internal/NFSv3/NFSv4-style errors back to NFSv2-compatible statuses.

## Main Responsibilities
- Handles NFSv2 NULL, GETATTR, SETATTR, LOOKUP, READLINK, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, STATFS, and obsolete/reserved procedures.
- Performs NFSv2-specific CREATE overloading for regular files, directories, FIFOs, char/block devices, truncation, and permission checks.
- Initializes read/readlink/readdir response pages and reserves reply buffer space for payloads.
- Maps unsupported or newer NFSD errors to NFSv2 status values through `nfsd_map_status()`.
- Defines `nfsd_procedures2[]` with decode/encode/release callbacks, argument/result sizes, reply cache policy, XDR result sizing, and procedure names.

## Key Data Structures and Interfaces
- Procedure arguments and responses are stored in `rqstp->rq_argp` and `rqstp->rq_resp`.
- Handlers operate mostly through `svc_fh`, `nfsd_attrs`, and shared VFS helpers such as `nfsd_lookup()`, `nfsd_read()`, `nfsd_write()`, `nfsd_create()`, `nfsd_unlink()`, `nfsd_rename()`, and `nfsd_statfs()`.
- `nfsd_version2` exports the NFSv2 service version descriptor with per-CPU procedure counters and `nfsd_dispatch()`.

## Important Behavior
NFSv2 has limited error vocabulary, so bad/no filehandle maps to stale, wrongsec/xdev/file-open maps to access, symlink-not-dir maps to notdir, and generic symlink/wrong-type maps to I/O.

SETATTR contains compatibility logic for old clients that set both atime and mtime to a value near current time. If explicit timestamp setting would fail, it converts the request to “set to now” semantics.

CREATE is intentionally complicated because NFSv2 overloads file creation and special-file semantics. It locks the parent, composes a child filehandle, infers type when absent, handles existing special files as permission checks, consumes `ATTR_SIZE` as device number for special files, and truncates existing regular files.

READ and WRITE clamp counts to NFSv2 maximums and available response buffer space. Jukebox errors set `RQ_DROPME` so the RPC can be dropped rather than replied to in selected cases.

READDIR builds a single-page XDR dirlist and stores cookie offsets for later patching by `nfssvc_encode_nfscookie()`.

## Dependencies
Depends on NFSD cache policy definitions, NFSv2 XDR helpers, common NFSD VFS helpers, filehandle helpers, tracepoints, Linux namei/create helpers, and SunRPC service procedure descriptors.

## Risks and Subtleties
NFSv2 protocol compatibility drives behavior that looks unusual from modern VFS semantics, especially CREATE type inference, timestamp handling, and special-file treatment. Refactors must preserve wire-visible quirks.

Several handlers transfer ownership of decoded filehandles and must call `fh_put()` on argument and/or response handles at the correct point. Release callbacks in the procedure table complete cleanup for successful response handles.
