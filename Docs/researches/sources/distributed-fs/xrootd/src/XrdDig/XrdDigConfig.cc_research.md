## sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.cc

### Purpose
This file configures digFS path exposure. It builds the remapping template under `XRDADMINPATH`, processes optional `dig.*` configuration directives, configures authorization, creates locate responses, validates exported roots, maps logical dig paths to real admin files, and audits allowed or denied access.

### Important APIs, Types, and Functions
- `XrdDig::Config` is the global `XrdDigConfig` instance.
- `Configure(const char *cFN, const char *parms)` parses the auth-file parameter, processes config, initializes `Auth`, sets locate responses, stats root, and validates `conf/core/logs/proc` exported roots.
- `GenAccess` returns visible top-level entries for a client based on authorization and available exported roots.
- `GenPath` validates top-level prefixes, authorizes the client, applies `/proc` safety checks, audits access, and returns a `strdup` real path generated from `fnTmplt`.
- `GetLocResp` returns hostname or IP locate responses.
- `StatRoot` copies cached root stat data.
- Private `AddPath`, `Empty`, `ValProc`, `xacf`, and `xlog` implement `dig.addconf` and `dig.log` directives.

### Control Flow
Initialization requires `XRDADMINPATH`, creates a template like `<admin>/.xrd/=/%s`, deletes stale `conf/etc` exports, tokenizes the first digFS parameter as the auth file, optionally parses a config file for `dig.addconf` and `dig.log`, and initializes authorization. It then prepares locate responses from local host/port and stats whether each protected prefix exists under the template.

Path generation maps a logical name to one of `conf`, `core`, `logs`, or `proc`, checks availability and authorization, performs extra proc traversal checks, audits if the target is a file and logging is enabled, formats the real path, and appends a slash for directory opens.

### State and Persistence
Persistent filesystem effects include symlink creation through `XrdOucUtils::ReLink` for `dig.addconf`, cleanup of stale `conf/etc`, and use of admin-path exports. Runtime state includes `fnTmplt`, locate response strings and lengths, `rootStat`, `pTab[].isOK`, and logging booleans. Authorization state lives in `XrdDigAuth`.

### Dependencies and Integration Points
This file depends on XrdOuc stream/tokenizer/env utilities, XrdNet address formatting, XrdSys logging/error conversion, `XrdDigAuth`, and POSIX filesystem calls. `XrdDigFS` calls `GenAccess`, `GenPath`, `GetLocResp`, and `StatRoot` for every user-facing operation.

### Risks and Edge Cases
`fnTmplt` and locate response strings are `strdup` allocations with process-lifetime ownership. `Configure` returns success even if `ConfigProc` cannot open the config file due to `return 1`, which may be intentional but is suspicious. `GenAccess` iterates `sizeof(aOK)-1`, relying on `bool` size and enum count. `ValProc` tries to prevent symlink traversal under proc but accepts shallow proc paths and only checks components after a certain depth. `AddPath` opens source paths read-only and may reject directories that need execute-only traversal. The locate response construction depends on environment `XRDPORT`.

### Test Signals
Tests should cover missing/long `XRDADMINPATH`, no parameters, auth file failures, `dig.addconf` target name derivation, rejection of target names containing `/`, `dig.log` combinations, top-level listing by authorization, denied audit logging, locate response for hostname/IPv4/IPv6, and proc symlink escape prevention.
