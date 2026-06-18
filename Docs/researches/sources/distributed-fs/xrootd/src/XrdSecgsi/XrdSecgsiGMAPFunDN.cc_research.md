# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiGMAPFunDN.cc

## Purpose

`XrdSecgsiGMAPFunDN.cc` implements a DN-to-user mapping plugin for the GSI protocol. It exports `XrdSecgsiGMAPFun`, the dynamic symbol loaded by `XrdSecProtocolgsi::LoadGMAPFun`, and maps certificate distinguished names to local user names using a simple configuration file with exact, prefix, suffix, or contains match rules.

## Important APIs, types, and functions

- `XrdVERSIONINFO(XrdSecgsiGMAPFun, secgsigmap)` publishes plugin version metadata.
- `XrdSecgsi_Match` enumerates match types: full, begins, ends, and contains.
- `XrdSecgsiMapEntry_t` stores a match value, target user, and match type.
- Static `gMappings` is an `XrdOucHash<XrdSecgsiMapEntry_t>` storing configured mappings.
- `FindMatchingCondition` is the hash apply callback used to scan non-exact mappings and stop on first match.
- `XrdSecgsiGMAPFun(const char *dn, int now)` is both initializer and mapper. `now <= 0` treats `dn` as the initialization parameter string and calls `XrdSecgsiGMAPInit`; `now > 0` treats `dn` as an actual distinguished name and returns a newly allocated mapped username or null.
- `XrdSecgsiGMAPInit(const char *parms)` parses `[cfg]|[d|dbg|debug]`, initializes plugin-local logging/tracing, resolves config path from parameters or `XRDGSIGMAPDNCF`, reads mappings, and populates `gMappings`.

## Control flow

The main protocol calls the plugin once with `now == 0` during loading. Initialization parses pipe-separated tokens; debug tokens enable `TRACE_Authen`, and the remaining token is the config file path. If no path is supplied, `XRDGSIGMAPDNCF` is used. The config file is read line by line, ignoring short lines and comments. Each valid line is parsed as `<pattern> <user>`.

Pattern syntax is compact:

- `^value` means DN begins with `value`.
- `value$` means DN ends with `value`.
- `value+` means DN contains `value`.
- Otherwise, the entry is a full-pattern match using `XrdOucString::matches`.

During authentication, `XrdSecProtocolgsi::QueryGMAP` calls this function with the end-entity DN and current timestamp. The plugin first tries `gMappings.Find(dn)`. If no exact hash key exists, it allocates a temporary match probe and applies `FindMatchingCondition` across the hash until a rule matches. On success it returns a heap-allocated `char[]` username to the main protocol, which caches it in `cacheGMAPFun`.

## State and persistence behavior

Mapping rules persist in the static `gMappings` hash for the life of the process. The plugin also creates static logger/tracer objects, with `dnTrace` allocated during initialization. It reads one config file at initialization and does not reload it by itself; any cache expiration in the main protocol re-runs mapping against the in-memory mapping table, not the file.

Returned usernames are allocated with `new char[]`; this matches the main protocol's use of `SafeDelArray` on cached GMAP plugin results. The temporary probe allocated in the non-exact path is not deleted in the visible implementation, which creates a per-lookup leak.

## Dependencies and integration points

The plugin depends on `XrdOucHash`, `XrdOucString`, `XrdOucTrace`, `XrdSysError`, `XrdSysLogger`, XRootD version metadata, and standard C file I/O. The main integration point is dynamic loading via `XrdSecProtocolgsi::LoadGMAPFun` and server configuration `-gmapfun:<plugin>` plus optional `-gmapfunparms:<cfg>|debug`.

The local `CMakeLists.txt` builds this source as `XrdSecgsiGMAPDN-${PLUGIN_VERSION}` and links it against `XrdUtils`.

## Risks and edge cases

- In the exact-match path, the code allocates `name` using `mc->val.length() + 1` and copies `mc->val`, not `mc->user`. That appears to return the pattern/DN rather than the mapped username for exact hash hits. Non-exact matches return `mc->user`.
- The non-exact lookup allocates `new XrdSecgsiMapEntry_t` and never deletes it.
- `gMappings.Add(p, ...)` keys all entries by the stripped pattern. Exact lookup only works when the DN string exactly equals a configured key; wildcard-style `matches` rules are only reached after exact lookup misses.
- Config parsing uses whitespace splitting via `sscanf`, so DN patterns containing spaces cannot be represented directly.
- Rule priority for scanned mappings depends on hash apply order, not file order. If multiple prefix/suffix/contains rules match, selected user may be order-dependent.
- Reinitialization does not clear `gMappings`, so repeated init calls can accumulate stale mappings.
- The plugin returns `(char *)-1` on init failure through `XrdSecgsiGMAPFun`, a sentinel expected by `LoadGMAPFun`; normal callers must not treat it as a username.

## Test signals

Tests should load the plugin through `LoadGMAPFun`, initialize from a temp config file, and verify exact, begins, ends, contains, and no-match behavior. A regression test should confirm whether exact matches return the configured user or the DN/pattern; the current code suggests the latter. Tests should verify `XRDGSIGMAPDNCF` fallback, debug parameter parsing, comments/blank lines, malformed lines, repeated init behavior, and memory behavior under repeated non-exact lookups.
