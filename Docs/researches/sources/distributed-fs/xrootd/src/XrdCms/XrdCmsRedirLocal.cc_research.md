# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.cc

Purpose: implements a CMS client plugin that can convert eligible redirects to local `file://` redirects when both client and selected target are on private networks.

Important APIs/functions: exported `XrdCmsGetClient()` constructs the plugin. Constructor wraps a native remote CMS finder. `Configure()` loads local redirect settings and configures the native finder. `loadConfig()` parses `xrdcmsredirlocal.readonlyredirect`, `xrdcmsredirlocal.httpredirect`, `xrdcmsredirlocal.localroot`, and fallback `oss.localroot`. `Locate()` delegates normal locate, then conditionally rewrites the response to a local file URL. `Space()` delegates.

Control flow: `Locate()` first detects possible localroot redirect loops and falls back to regular CMS locate after stripping localroot if `tried=localhost` is present. It then calls native locate, blocks HTTP unless enabled, requires private target and private client, checks client URL/local redirect capabilities for non-HTTP, filters unsafe write flags when read-only mode is configured, and sets `Resp` to `file://localroot + path` before returning `SFS_REDIRECT`.

State and persistence: plugin state is `nativeCmsFinder`, `readOnlyredirect`, `httpRedirect`, `localroot`, and logger. Config is read from the xrootd config file only at configure time.

Dependencies/integration: wraps `XrdCmsFinderRMT` through `XrdCmsClient`; uses `XrdOucStream`, `XrdNetAddr`, `XrdOucEnv` security environment, SFS flags, and version metadata.

Risks: `EnvInfo` and `secEnv()->addrInfo` are assumed non-null. Config boolean parsing treats any value containing `true` as true. Flag filtering uses numeric thresholds and a hard-coded HTTP stat flag (`0x20000000`), which can drift from SFS definitions. Loop handling depends on `tried=localhost` string presence.

Test signals: plugin configure tests with missing/relative localroot, private/public client-target matrix, HTTP enabled/disabled behavior, read-only flag filtering, localroot loop handling, and delegated `Space`/forwarding methods.
