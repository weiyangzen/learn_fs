# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.cc

## Purpose

`XrdPssUrlInfo.cc` implements request URL metadata handling for PSS. It carries the target path, client CGI, proxy-added CGI, trace identity, and optional compact identity string used when constructing upstream URLs.

## Important APIs, Types, And Functions

- Static `XrdPssUrlInfo::MapID` toggles whether `setID()` uses the security entity unique ID instead of parsing the trace identifier.
- Local `copyCGI()` copies client CGI while stripping `xrd.*` and `xrdcl.*` keys that can interfere with xrootd upstreams.
- The constructor captures user CGI from `XrdOucEnv`, extracts `XrdSecEntity::ueid` and `tident`, falls back to `"unk.0:0@host"`, and builds optional `pss.tid=<tident>` suffix CGI.
- `addCGI(prot, buff, blen)` appends query text appropriate for the upstream protocol. For xroot-family protocols it strips sensitive xroot CGI keys and includes proxy suffix CGI; for other protocols it forwards only the client CGI.
- `Extend(cgi, cgiln)` appends additional suffix CGI with an ampersand separator.
- `setID(tid)` creates a compact ID from either the security entity ID or the file descriptor portion of a trace identity.

## Control Flow

Construction prepares immutable per-request metadata. When the proxy builds an upstream URL, `addCGI()` first determines whether the target protocol is xroot-family via `XrdPssUtils::is4Xrootd()`. If no CGI is needed, it emits an empty suffix. Otherwise it adds `?`, filters or copies user CGI, and appends proxy suffixes only for xroot-family targets. `setID()` is called when the upstream URL needs an identity prefix; it prefers mapped entity IDs when configured, otherwise parses `pid:fd@host` from `tident`.

## State And Persistence

State is per `XrdPssUrlInfo` instance except for static `MapID`. The object stores borrowed pointers to path, user CGI, and trace identity, plus local fixed-size buffers for ID and suffix CGI. If a session ID is obtained through `setID(XrdOucSid*)`, the destructor releases it.

## Dependencies And Integration Points

The implementation uses `XrdOucEnv`, `XrdOucSid`, `XrdSecEntity`, and `XrdPssUtils`. It is configured by `XrdPssConfig.cc` through `setMapID(true)` when client persona mapping is active and is used by proxy request paths that construct upstream URLs and preserve request identity.

## Risks And Edge Cases

- `CgiSfx` is fixed at 512 bytes; long trace identifiers or extra CGI can be rejected.
- `addCGI()` must be called with a large enough buffer; it returns false instead of truncating.
- `copyCGI()` strips only CGI keys beginning at component boundaries; unusual encoding or capitalization is not normalized.
- Borrowed `XrdOucEnv` strings and path pointers must remain valid for the request lifetime.
- `setID()` depends on trace identifier format and silently produces an empty ID on unexpected format or length.

## Test Signals

Tests should cover no CGI, user CGI only, suffix CGI only, xroot and non-xroot protocols, stripping `xrd.*` and `xrdcl.*`, buffer exhaustion, `Extend()` separator behavior, mapped entity IDs, trace-ID parsing, and session-ID release.
