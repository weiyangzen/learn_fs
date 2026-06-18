# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfig.cc

## Purpose

`XrdOfsConfig.cc` implements configuration for the OFS filesystem. It parses `ofs.*`, `all.role`, `all.subcluster`, `all.export`, and `oss.defaults` directives; loads and configures plugins; establishes roles, CMS redirection, authorization, checksums, prepare handlers, event notification, TPC, POSC, checkpointing, xattrs, forwarding, trace settings, and effective mode masks.

## Important APIs, Types, and Functions

- `getVersion()` returns the compiled XRootD version string.
- `Configure()` is the startup coordinator. It reads the config file, invokes directive parsers through `ConfigXeq()`, loads plugins with `XrdOfsConfigPI`, initializes CMS/finder/balancer, event receivers, TPC, checkpointing, POSC, stats role, and displays the effective configuration.
- `Config_Display()` prints effective config, plugin display output, forwarding setup, and notify settings.
- `ConfigPosc()` builds the POSC recovery log path, creates `XrdOfsPoscq`, rehydrates pending POSC records, either holds incomplete files through retired handles or unpersists them.
- `ConfigRedir()` creates CMS finder/balancer objects depending on manager/server/proxy/subcluster role.
- `ConfigTPC()` phase 1 prepares credential/reproxy paths and monitors; phase 2 resolves OSS reproxy support and starts `XrdOfsTPC`.
- `ConfigTPCDir()` creates/protects TPC credential/reproxy directories and clears stale files.
- `ConfigXeq()` dispatches directives to parser functions or plugin parser entries.
- Parser methods: `xcrds`, `xcrm`, `xdirl`, `xexp`, `xforward`, `xmaxd`, `xnmsg`, `xnot`, `xpers`, `xrole`, `xtpc`, `xtpcal`, `xtpcr`, `xtrace`, `xatr`.
- `theRole()` maps role option bits to a human-readable role.

## Control Flow

Startup begins by requiring `XrdNetIF` and scheduler pointers from `EnvInfo`, setting defaults, and creating the plugin configurator. The config file is scanned once; recognized OFS and role directives are parsed, while export/default directives are pre-scanned to infer writable/read-only OSS capability. After parsing, the code exports role/redirect environment variables, defaults proxy plugins to `libXrdPss.so` when appropriate, and runs early TPC/event-receiver setup before plugin loading.

Plugin loading establishes `XrdOfsOss`, OSS feature flags, checksum manager, prepare handler, authorization, and optional FSctl handlers. Then redirection, FSctl, event notification, forwarding validation, proxy detection, checkpoint initialization, POSC recovery, stats, and display occur in that order. POSC is intentionally last because it needs a working filesystem.

Directive parsers are mostly single-purpose and return `0`/nonzero for success/failure. Some parsers are cumulative (`trace`, `forward`, `notify` event masks), while others replace previous state (`xattr`, `role`, redirect targets).

## State and Persistence Behavior

Configuration mutates long-lived `XrdOfs` members: role bits, mode masks, plugin pointers, event object, forwarding targets, POSC settings, TPC redirect hosts, xattr limits, and checksum behavior. It also exports environment variables used by other components (`XRDROLE`, `XRDREDIRECT`, `XRDOFS_FWD`, `XrdOss*`, authorization pointer, cache marker).

Persistent startup recovery happens in `ConfigPosc()` for POSC logs and in `XrdOfsConfigCP::Init()` for checkpoints, called from `Configure()`. TPC credential/reproxy directories are created and cleaned. Checkpointing is skipped for managers and disabled for proxy OSS backends.

## Dependencies and Integration Points

This file integrates with `XrdOfsConfigPI` for plugin loading/configuring, `XrdOss` features, `XrdCmsFinderRMT/TRG` or CMS plugin constructors, `XrdOfsTPCConfig`, `XrdOfsTPC`, `XrdOfsEvs`, `XrdOfsEvr`, `XrdOfsPoscq`, `XrdOfsStats`, `XrdAccAuthorize`, `XrdOucStream`, `XrdOuca2x`, `XrdOucUtils`, `XrdOucNSWalk`, and network utilities. It is the bridge between text config and the runtime behavior implemented in `XrdOfs.cc`.

## Risks and Edge Cases

- Configuration ordering is critical: TPC phase 1 happens before plugin load, TPC phase 2 after OSS features, POSC last, checkpoint skipped for managers/proxies.
- Several parser branches contain subtle logic hazards: `xtpc require` has a `break` before reading the auth token, making subsequent `Require()` code unreachable; `xtpcal` uses `if (i > numopts)` instead of `i >= numopts` and then immediately enters an error block, which appears to reject even valid options.
- `xnot()` allocates a new `XrdOfsEvs` after deleting any previous one; errors after partial parse can leave old state intact until replacement.
- `ConfigTPCDir()` deletes all files and links in the chosen directory at startup; path construction and permissions are safety-critical.
- POSC recovery may unpersist files on startup depending on hold time and queue records.
- If `EnvInfo` is null, later uses such as `EnvInfo->GetPtr("XrdFSCtl_PC*")` rely on earlier setup; startup environments must supply expected pointers.
- `umask` is set globally from creation masks, affecting process-wide file creation.

## Test Signals

Configuration tests should parse each directive and invalid option, verify mode-mask transformations, role combinations, forwarding display and disable conditions, notify and notifymsg setup, xattr limits, TPC redirect parsing including IPv6/localhost/cgi, TPC directory cleanup permissions, plugin feature flags, proxy behavior, checkpoint/POSC enablement, and startup POSC recovery. Regression tests should specifically cover `xtpc require` and `xtpcal allow` parsing behavior.
