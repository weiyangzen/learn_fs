# File Research: sources/os/linux/linux-stable/fs/lockd/svcproc.c

## Summary
NLMv1 and NLMv3 server procedures. It is the older hand-written procedure layer over `nlm_args` / `nlm_res`, sharing the same lock core as NLMv4 but with v1/v3 status constraints and legacy XDR.

## Main APIs
Defines sync and async forms of `TEST`, `LOCK`, `CANCEL`, `UNLOCK`, `GRANTED`, `GRANTED_RES`, `SM_NOTIFY`, `SHARE`, `UNSHARE`, `NM_LOCK`, `FREE_ALL`, and procedure tables for `nlmsvc_version1` and `nlmsvc_version3`.

## Behavior
`nlmsvc_retrieve_args()` resolves the caller host, optionally starts NSM monitoring, opens the file in the mode implied by the requested lock, fills missing `file_lock` fields, and installs `nlmsvc_lock_operations`. Procedure handlers delegate to `svclock.c` and `svcshare.c`, then release lock owners, hosts, and files.

## State and Data Flow
`cast_status()` maps internal and v4-ish statuses into values legal for v1/v3. Async `*_MSG` procedures allocate an `nlm_rqst`, run the same underlying operation into its response, then send a callback result before returning a void reply.

## Dependencies
Legacy XDR codecs from `xdr.c`, `nlmsvc_dispatch()` from `svc.c`, lock/share helpers, NSM monitoring, host reboot processing, and SunRPC async reply support.

## Risks
Older protocol versions cannot express all internal failures, so status folding can hide stale file handles or deadlocks. The callback implementation is “async” only in the sense that the callback reply is sent separately; comments note ordering may be surprising to clients.
