# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.cc

## Purpose

`XrdCmsConfig.cc` implements cmsd startup and runtime configuration. It owns global CMS objects, parses `cms.*`/legacy directives, establishes role, networking, admin sockets, cache/base-filesystem behavior, OSS/name/security plugins, exported paths, scheduling and space policy, and starts the background threads that make a configured CMS service active.

## Important APIs and functions

- `Configure0()` imports protocol bootstrap state: logger, trace logger, host/program/instance names, TCP port, scheduler, admin path/mode, debug flag, and inherited environment.
- `Configure1()` handles command-line role overrides, finds and scans the config file, pre-scans role if needed, processes configuration directives, computes role strings/types, exports `XRDROLE` and `XRDROLETYPE`, validates role/port combinations, and applies proxy/metric warnings.
- `Configure2()` completes phase-two setup: cache init, admin socket creation, stable system id generation, login CGI environment, N2N/OSS/prep/baseFS setup, manager/server setup, CMS state initialization, manifest append, and scheduling of `DoIt()`.
- `ConfigXeq()` dispatches directives to individual handlers and separates dynamic-safe directives from startup-only directives.
- `DoIt()` starts notification, prepare, supervisor, admin, manager, state-monitor, ping-clock, and service-enable flows.
- `ConfigDefaults()` initializes all defaults for role flags, delays, scheduling, disk thresholds, plugin paths, sockets, caches, prep state, and timezone.
- `ConfigN2N()`, `ConfigOSS()`, `Manifest()`, `MergeP()`, `setupManager()`, `setupServer()`, and `setupSid()` are the main setup helpers.
- Directive handlers map config syntax into `XrdCmsConfig` fields and subsystem calls for allow/blacklist/cid/delay/dfs/export/fsxeq/fxhold/manager/mode/nbsendq/perf/ping/prep/repstats/role/sched/security/space/subcluster/superport/trace/vnid behavior.

## Control flow

Startup is staged. Phase 0 receives host process state from `XrdProtocol_Config`. Phase 1 parses arguments and configuration enough to determine role and validate base parameters. If the role was not supplied on the command line, it pre-scans only `all.role`/`olb.role`; then it performs the full config scan and dispatches recognized directives by stripping the prefix and calling `ConfigXeq()`.

Phase 2 performs operations that require a resolved role and parsed settings. Managers initialize the cache, all roles create an admin socket path, all roles derive `mySID`, optional N2N and OSS plugins are loaded, the base filesystem and prepare queue start, manager/server setup functions start role-specific resources, `CmsState` is initialized, and an environment manifest can be appended with prefix/admin/cluster id data. On success the object schedules itself as an `XrdJob`, and `DoIt()` starts the long-running service threads.

Directive handlers are mostly small parsers. Manager-only directives silently no-echo on incompatible roles. Numeric conversions use `XrdOuca2x`; plugin/library parsing uses `XrdOucUtils::parseLib`; manager host parsing uses `XrdCmsUtils::ParseManPort()`/`ParseMan()`; export/default path parsing delegates to `XrdOucExport`; conditional directives use `XrdOucUtils::doIf()`.

## State and persistence behavior

The file defines process-global CMS objects in namespace `XrdCms`: `theEnv`, `Admin`, `baseFS`, `Config`, `Say`, `Trace`, and `Sched`. Configuration state is stored as fields on the global `Config` instance. Most strings are heap-owned `char *` values managed by explicit `strdup()`/`free()`, while many role/environment pointers are borrowed or duplicated depending on source.

Persistent side effects are limited but important: named admin/notification sockets are created under `AdminPath`; `Manifest()` appends `&pfx=`, `&ap=`, and `&cn=` data to an environment file named by `xrdEnv->Get("envFile")`; external programs and plugins are loaded or validated; and environment variables such as `XRDROLE`, `XRDROLETYPE`, `XRDREDIRECT`, `XRDOSSTYPE`, and `XRDOSSCSCAN` are exported.

## Dependencies and integration points

This file is the integration hub for CMS startup. It touches protocol bootstrap, scheduler/jobs/threads, network sockets and addresses, security, OSS, name-to-name loaders, exports, stream parsing, base filesystem mode, cache, cluster, manager, meter, prepare queue, request queue, supervisor, state monitor, trace, blacklist, and utility functions. `XrdCmsCluster` consumes many fields set here: scheduling weights, max load/delay, disk thresholds, lookup/service/suspend/peer delays, server minimums, and role flags.

## Risks

- The parser is broad and role-sensitive; regression tests need both accepted and ignored directives for manager, server, supervisor, peer, proxy, and meta-manager modes.
- Memory ownership is manual and mixed. Repeated dynamic directives free some old strings but not every startup field is designed for dynamic reconfiguration.
- `xnbsq()` appears to compare the literal string `"val"` to `"none"` instead of comparing the parsed `val`, which would prevent `maxq none` from working as described.
- `xrole()` peer handling sets `xPeer`/`xSolo` based on `xServ - 1`; this may be intentional old-style negative marker logic, but the expression is subtle enough to merit a targeted role test.
- `Configure1()` role resolution has legacy negative markers and command-line override behavior; accidental sign changes can alter role defaults.
- `Manifest()` appends unescaped path and cluster-id fragments to an environment file. Inputs containing separators should be checked against the consumer contract.

## Test signals

Useful signals include startup tests for each role; config parsing tests for every directive family; dynamic reconfiguration tests for `delay`, `fxhold`, `ping`, `sched`, `space`, and `trace`; manager list and subcluster domain validation; DFS option combinations; export merging into `PathList` and `myPaths`; OSS/N2N plugin error handling; admin path creation and warning behavior; scheduler policy derivation; and smoke tests that phase 2 starts the expected threads and state for manager/server/peer/proxy combinations.
