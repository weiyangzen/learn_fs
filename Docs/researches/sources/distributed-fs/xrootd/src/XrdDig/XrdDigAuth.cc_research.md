## sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.cc

### Purpose
This file implements authorization for digFS administrative information exposure. It reads a dig authorization file, builds an in-memory ACL list, refreshes it when the file changes, and authorizes clients against protocol, name, host, virtual organization, role, and group fields.

### Important APIs, Types, and Functions
- `XrdDig::Auth` is the global `XrdDigAuth` instance used by configuration and filesystem code.
- `XrdDigAuth::Configure(const char *aFN)` stores the auth-file path and performs initial setup.
- `XrdDigAuth::Authorize(const XrdSecEntity *client, XrdDigAuthEnt::aType aType, bool aVec[])` refreshes when needed, matches the client against ACL records, and returns either a specific access decision or fills the access vector.
- `Parse(XrdOucStream&, int)` parses a single auth file line into `XrdDigAuthEnt`.
- `Refresh()` deletes and rebuilds the ACL list under the auth mutex.
- `SetupAuth(...)` opens, stats, reads, and validates the file, then logs initialization or refresh status.
- `OkGrp` matches a group token inside a space-separated group list; `Squash` converts `\s` escapes to spaces.

### Control Flow
Authorization takes the mutex, checks whether the next scheduled `authCHK` refresh time has passed, stats the auth file, and refreshes if missing, changed, or previously present but removed. It resets the caller's access vector when supplied, checks global resource availability through the summary `accOK` mask, and then scans ACL records. A record matches only when protocol matches and all specified entity predicates match. A matched record returns the requested access bit or copies all bits into `aVec`.

Parsing first consumes access tokens such as `all`, `conf`, `core`, `logs`, `proc`, and negated forms like `-logs`, then expects an auth protocol. Entity selectors are encoded by first character using `"nhorg"` for name, host, VO, role, and group. Values are packed into one allocated `rec` buffer and `eChk` pointers are relocated into that buffer.

### State and Persistence
Runtime state is in `authFN`, `authTOD`, `authCHK`, `authList`, and the summary `accOK` mask, protected by `authMutex`. The auth file is persistent external configuration. Missing auth files suspend access but are not necessarily fatal. Refresh scheduling uses short backoffs of 5, 30, or 60 seconds depending on stat/read state.

### Dependencies and Integration Points
The file depends on `XrdSecEntity`, `XrdNetAddrInfo`, `XrdOucStream`, `XrdSysError`, and `XrdSysE2T`. `XrdDigConfig` calls `Auth.Configure` during digFS initialization and `Auth.Authorize` when generating listings or mapping logical dig paths to real paths.

### Risks and Edge Cases
`Configure` stores `strdup(aFN)` into a `const char *` and never frees it. The ACL list is singly linked and refreshed wholesale, which is simple but can briefly make access unavailable on parse errors. `OkGrp` uses substring search with only trailing space or end checks, so a match at the middle of another group name may be possible if not preceded by a delimiter. Host comparison depends on `addrInfo->Name("")` and exact string equality. `Authorize` dereferences `client->addrInfo` when host matching without checking it. Parsing uses a fixed 4096-byte value buffer.

### Test Signals
Tests should cover valid and invalid auth lines, negated access tokens, `all`, each entity selector, escaped spaces, missing auth file behavior, refresh after file mtime change, group boundary matching, and concurrent authorization during refresh.
