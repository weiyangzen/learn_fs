# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_strerror.c

## Purpose
Provides NFS-specific kernel printf/cmn_err wrappers that support syslog-style `%m` substitution for selected errno values.

## Key Elements
`nfs_perror` and `nfs_cmn_err` accept an errno value plus a printf-style format, expand every `%m` sequence into a human-readable error string with `expand_format_string`, then emit through zone-aware `vzprintf` or `vzcmn_err`. `nfs_strerror` maps a small errno subset used by NFS paths, including permissions, lookup, I/O, quota, stale handle, read-only filesystem, and memory errors.

The expansion function uses a fixed 1024-byte temporary buffer, falls back to `error %d` when no string is known or the named string will not fit, and emits a truncation warning if the expanded message cannot fit.

## Dependencies
Uses NFS headers, kernel varargs, zone-aware printf/cmn_err routines, errno constants, and simple string formatting helpers.

## Behavior/Risks
This is not a general `strerror` implementation; unknown errno values intentionally become `error N` or no message if space is exhausted. The `%m` expander is simple and only treats literal `%m` specially, so format-string behavior should not be extended casually. Buffer sizing and `strlen(buf)` use during construction make truncation behavior sensitive to edits.
