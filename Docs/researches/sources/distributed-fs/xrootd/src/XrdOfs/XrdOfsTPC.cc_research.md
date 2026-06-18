# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.cc

## Purpose

`XrdOfsTPC.cc` implements the high-level OFS third-party-copy control path. It validates TPC CGI/environment fields, enforces configured authentication and path restrictions, creates origin-side authorization grants, creates destination-side copy jobs, exports runtime feature flags, and ties configuration in `XrdOfsTPCConfig` to `XrdOfsTPCAuth`, `XrdOfsTPCJob`, and `XrdOfsTPCProg`. The source was read as a complete 699-line implementation.

## Important APIs, Types, and Functions

The file defines static `XrdOfsTPC` methods: `AddAuth`, `Allow`, `Authorize`, `Init`, `Require`, `Restrict`, `Start`, `Validate`, plus helpers `Death`, `Fatal`, `genOrg`, `getTTL`, `Screen`, and `Verify`. It owns the `XrdOfsTPCParms` globals `fcAuth`, `fcNum`, `tpcOK`, `encTPC`, `tpcMon`, and `Cfg`, and defines the private allow-list class `XrdOfsTPCAllow`. Static authorization lists include `AuthDst`, `AuthOrg`, `ALList`, `RPList`, `fsAuth`, and credential path `cPath`.

## Control Flow

`Start()` finalizes path-restriction defaults, installs a default transfer command of `xrdcp --server` when none is configured, initializes the transfer-program pool, starts the authorization TTL thread, exports `XRDTPC`, and marks TPC as enabled. `Authorize()` handles source-open authorization. If the request has destination and no origin, this server is the origin granting a rendezvous authorization after local read authorization and origin auth screening. If the request has origin and no destination, this server is the destination validating that the origin granted access, checking allow-list host/DN/group/VO restrictions, finding the matching `XrdOfsTPCAuth`, and returning it. `Validate()` handles write-side requests that ask the destination to fetch from a source. It validates delegated credentials, source URL pieces, source LFN semantics, stream count, rendezvous CGI, optional reproxy path, and finally creates an `XrdOfsTPCJob`.

## State and Persistence Behavior

All state is process-local. Authorization requirements, credential-forwarding auth table, allow-list entries, path restrictions, and TPC configuration are static process state. `Validate()` creates heap `XrdOfsTPCJob` instances containing copy metadata, forwarded credentials, and optional reproxy paths. `Death()` and `XrdOfsTPCInfo` cleanup can remove partially created destination files when `Cfg.autoRM` is enabled. No durable database is maintained; rendezvous state lives in the in-memory auth queue.

## Dependencies and Integration Points

The file integrates with `XrdAccAuthorize` for read authorization, `XrdSecEntity` identity fields, `XrdOucTPC` CGI helpers, `XrdOucEnv` request environment, `XrdOucPList`/`XrdOucTList` restrictions, `XrdOss` file cleanup, `XrdOfsStats`, `OfsEroute`, `OfsTrace`, and the TPC helper classes. It exports `XRDTPC` and `XRDTPCDLG` environment signals consumed by xrootd clients and transfer tooling.

## Risks and Edge Cases

Security depends on exact CGI interpretation and canonical destination host matching. Allow-list matching is sensitive to identity fields and host DNS behavior. URL construction can fail on long LFN/CGI inputs. Delegated credential handling checks for GSI private-key material when required, but optional credentials can silently fall back to rendezvous tokens. `autoRM` cleanup uses `Args.Lfn` in one path even when comments refer to PFNs, so deletion behavior must be reviewed when path translation changes.

## Test Signals

Useful tests include origin and destination TPC handshakes; encrypted-auth requirement failures; allow-list host/DN/group/VO accept and reject cases; oversized CGI/LFN validation; delegated-credential required, optional, and GSI cases; `tpc.streams` clamping; reproxy path export; and `autoRM` failure cleanup.
