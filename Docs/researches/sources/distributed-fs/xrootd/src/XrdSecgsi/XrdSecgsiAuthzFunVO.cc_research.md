# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunVO.cc

## Purpose

`XrdSecgsiAuthzFunVO.cc` implements a simple VO-based authorization plugin for the GSI protocol. It propagates `entity.vorg` into the local Unix-style user and/or group fields according to CGI-formatted configuration parameters, with optional VO allow-list enforcement. It exports the standard authz plugin symbols consumed by `XrdSecProtocolgsi::LoadAuthzFun`.

## Important APIs and functions

- `XrdSecgsiAuthzInit(const char *cfg)`: parses plugin parameters from a CGI-style string, sets debugging, `vo2grp`, `vo2usr`, `valido`, and CN-to-user behavior, and returns `1` to request PEM/base64 credentials.
- `XrdSecgsiAuthzFun(XrdSecEntity &entity)`: validates `entity.vorg`, optionally checks it against `valido`, formats `entity.grps` from `vo2grp`, formats `entity.name` from `vo2usr`, or derives `entity.name` from the first `/CN=` component when configured to do so. It logs entity fields under a static mutex when debug is enabled.
- `XrdSecgsiAuthzKey(XrdSecEntity &entity, char **key)`: allocates a cache key by copying `entity.creds` and returns `entity.credslen`.
- Static configuration state in the anonymous namespace: `g_certificate_format`, `g_maxvolen`, `g_valido`, `g_vo2grp`, `g_vo2usr`, `g_debug`, and `g_cn2usr`.

## Control flow

The main GSI protocol loads this module as an authz function and calls `XrdSecgsiAuthzInit` with `-authzfunparms`. The init function first copies at most 2047 bytes and truncates at the first space to guard against accidental trailing protocol parameters, then parses the string using `XrdOucEnv`.

During authentication, the main protocol sets `Entity.creds` in PEM form because the init function returns `1`, optionally after VOMS extraction has filled `entity.vorg`. `XrdSecgsiAuthzKey` uses the entire PEM credential string as the authz cache key. On a cache miss, `XrdSecgsiAuthzFun` validates and rewrites selected entity fields. A nonzero return causes the main protocol to fail authentication.

`XrdSecgsiAuthzFun` first checks that `entity.vorg` exists, is no longer than 255 bytes, and is present in `g_valido` if an allow-list is configured. It then formats group and user strings with `snprintf` into a fixed buffer. If no `vo2usr` is configured and CN-to-user derivation is enabled, it tries to extract the text after `/CN=`, replace spaces with underscores, and assign it to `entity.name`.

## State and persistence behavior

All configuration is stored in process-wide static variables. `g_vo2grp`, `g_vo2usr`, and `g_valido` are heap-duplicated during init and are never freed in this file, which is acceptable for one-time plugin initialization but relevant to repeated load/unload tests. The plugin mutates `entity.name` and `entity.grps` by freeing existing values and assigning `strdup` results. It does not read or write files.

The cache key is a full copy of `entity.creds`, so authz cache persistence in the main protocol is scoped to the exact PEM credential text. This avoids collisions across different proxies but can be large and sensitive.

## Dependencies and integration points

The plugin depends on `XrdSecEntity`, `XrdOucEnv`, `XrdOucLock`, `XrdSysMutex`, and XRootD version metadata. It integrates with the GSI protocol's authz plugin loader through `XrdSecgsiAuthzFun`, `XrdSecgsiAuthzKey`, and `XrdSecgsiAuthzInit`. The local `CMakeLists.txt` builds it as `XrdSecgsiAUTHZVO-${PLUGIN_VERSION}` and links it against `XrdUtils`.

Expected configuration examples include `debug=1`, `valido=<comma-list>`, `vo2grp=<printf-format>`, and `vo2usr=<printf-format or *>`. `vo2usr=*` preserves `entity.name` as set by the GSI module.

## Risks and edge cases

- The CN-to-user derivation block appears to use `n`, the length of `entity.vorg`, as the null-termination index after copying from the CN. That likely truncates or mis-terminates the CN-derived username when VO length differs from CN length.
- The trailing-underscore cleanup loop initializes `cP` to the end of the string but checks `*cP` while decrementing `i`, which likely does not inspect the intended trailing characters. This should be tested and possibly fixed.
- `vo2grp` and `vo2usr` are used as `snprintf` format strings controlled by configuration. They are expected to contain one `%s`, but malformed or hostile format strings can produce unexpected formatting behavior.
- `XrdSecgsiAuthzKey` allocates `entity.credslen + 1` and calls `strcpy`, assuming `entity.creds` is NUL-terminated and at least `credslen` bytes. The main protocol provides PEM strings, but defensive tests should cover null or inconsistent lengths.
- `valido` matching uses substring search on a comma-prefixed allow-list. It prefixes the candidate VO with a comma but does not append a comma, so allow-list boundary behavior should be verified for names where one VO is a prefix of another.
- Static globals are not protected during init; the module assumes one-time initialization before concurrent auth calls.

## Test signals

Tests should cover missing VO, overlong VO, allowed/disallowed VO lists, `vo2grp`, `vo2usr`, `vo2usr=*`, CN-derived usernames, names with spaces, and repeated debug logging from concurrent threads. Cache-key tests should verify that the copied key length and contents match PEM credentials. Negative tests should include null `key`, null credentials, malformed config strings, long VO values, and potentially dangerous format strings. A focused unit test should catch the suspected CN truncation/trailing-underscore bugs.
