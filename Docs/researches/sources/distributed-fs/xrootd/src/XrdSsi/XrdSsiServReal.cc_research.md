# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.cc

## Purpose
`XrdSsiServReal.cc` implements the concrete client-side `XrdSsiService` that routes SSI requests to endpoint servers using `XrdCl::File` sessions. It manages session allocation, reusable resource caching, endpoint URL construction, stream entry allocation, and service shutdown.

## Important APIs and Functions
`ProcessRequest` is the main entry point. `Recycle` returns or deletes sessions. `Stop` implements service shutdown semantics. `StopReuse` removes a cached reusable session. Private helpers `Alloc`, `GenURL`, and `ResReuse` allocate/reinitialize sessions, build `xroot://` endpoint URLs, and handle reusable/discard resource options.

## Control Flow
`ProcessRequest` rejects empty resource names, checks the reusable cache under `rcMutex`, obtains a channel from global `sidScale`, builds an endpoint URL containing manager node, resource name, avoid list, affinity, user, CGI info, and optional user entry, then allocates a session and provisions it. Held reusable sessions are stored in `resCache` after provisioning starts. A cache hit calls `Run` on the existing session unless discard/retry semantics force unhold and replacement.

## State and Persistence
The service owns in-memory session pools only: `freeSes`, `freeCnt`, `freeMax`, `actvSes`, `doStop`, `manNode`, and `resCache`. No state is persisted. Reuse cache keys combine `rUser`, `"@"`, and `rName`.

## Dependencies and Integration Points
It integrates `XrdSsiResource`, `XrdSsiRequest`, `XrdSsiSessReal`, `XrdSsiRRAgent`, `XrdSsiScale`, `XrdSsiUtils`, and SSI tracing. It uses `ENOSR`/`ENOSPC` fallback for stream exhaustion and feeds endpoint URLs to `XrdSsiSessReal::Provision`.

## Risks and Test Signals
Important risks include cache/session lifetime under concurrent discard, URL buffer overflow, leaking a channel entry on early returns, and `Stop` deleting `this`. Tests should cover missing resource names, long URL fields, retry/discard cache bypass, reusable session reuse after open, provision failure recycling, free-list limits, immediate and delayed stop, and `StopReuse` racing with `Recycle`.
