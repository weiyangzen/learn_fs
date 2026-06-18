# File Research: sources/os/linux/linux-stable/fs/lockd/svc4proc.c

## Summary
NLMv4 server procedure implementation. It adapts generated `nlm4xdr_gen.h` types into legacy lockd `nlm_lock`, `nlm_cookie`, and `nlm_res` machinery, then wires all NLMv4 procedures into `nlmsvc_version4`.

## Main APIs
Procedures include `NULL`, `TEST`, `LOCK`, `CANCEL`, `UNLOCK`, `GRANTED`, async `*_MSG` callback forms, `GRANTED_RES`, `SM_NOTIFY`, `SHARE`, `UNSHARE`, `NM_LOCK`, and `FREE_ALL`.

## Behavior
Helper wrappers keep generated XDR structs first so RPC dispatch can cast them directly. `nlm4svc_lookup_host()` resolves callers and optionally starts NSM monitoring. `nlm4svc_lookup_file()` validates NFS file handle length and 64-bit lock range, opens a lockd file, fills VFS `file_lock`, and attaches lock-manager operations. Sync calls return encoded replies; async `*_MSG` procedures allocate an `nlm_rqst` and send callback replies with `nlm_async_reply()`.

## State and Data Flow
NLMv4 offsets and lengths are preserved as 64-bit values and mapped into `file_lock` ranges. Cookies are copied into fixed `NLM_MAXCOOKIELEN` storage for callback correlation. Share procedures synthesize a lock with `LOCKD_SHARE_SVID` and delegate conflict checks to `svcshare.c`.

## Dependencies
Generated NLMv4 XDR codecs, lockd host/file/NSM logic, `nlmsvc_lock()`, `nlmsvc_testlock()`, `nlmsvc_unlock()`, `nlmsvc_cancel_blocked()`, share helpers, and client grant callback handling.

## Risks
Range validation must reject wraparound beyond `OFFSET_MAX`. Every path that initializes an NLM lock owner must release it exactly once. Async callbacks take ownership of host references. V4-specific status mapping includes `nlm4_deadlock`, `nlm4_fbig`, `nlm4_stale_fh`, and `nlm4_failed`, unlike v1/v3.
