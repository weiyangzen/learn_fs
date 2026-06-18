# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.cc

## Purpose
`XrdSsiSfsConfig.cc` implements SSI plugin configuration. It parses `ssi.*` and `all.role` directives, initializes global SSI runtime objects, loads provider and optional CMS plugins, configures buffers and request limits, and obtains the server-side `XrdSsiService`.

## Important APIs and Functions
Public `Configure(const char *, XrdOucEnv *)` reads the config file and delegates to `Configure(XrdOucEnv *)` for phase-two initialization. Private functions include `ConfigCms`, `ConfigObj`, `ConfigSvc`, `ConfigXeq`, `Xlib`, `Xfsp`, `Xopts`, `Xrole`, and `Xtrace`.

## Control Flow
The file opens the config, captures SSI directives, validates that the role is server-compatible, validates `fspath` stacking requirements, then finds scheduler/environment/network objects. It creates buffer pools, configures CMS client/cluster behavior, loads `svclib` through `XrdSysPlugin`, resolves either `XrdSsiProviderServer` or `XrdSsiProviderLookup`, initializes the provider, and obtains the service unless running in CMS stat mode.

## State and Persistence
Configuration writes process-global state only: `SsiCms`, `Sched`, `BuffPool`, `FSPath`, `myIF`, `Provider`, `Service`, logger, response wait, request size limits, `fsChk`, and `detReqOK`. No config changes are persisted to disk.

## Dependencies and Integration Points
It integrates `XrdCms`, `XrdOucStream`, `XrdOuca2x`, `XrdSysPlugin`, `XrdSsiProvider`, `XrdSsiCms`, `XrdSsiFileReq`, `XrdSsiFileSess`, `XrdNetIF`, and XRootD versioning. It is used by both filesystem plugin startup and stat-info plugin startup.

## Risks and Test Signals
Risks include plugin symbol mismatches, incorrect role parsing, null environment pointers, option parsing bugs, and a likely typo where `detReqOK` is set from `fAut >= 0` instead of `fDet >= 0`. Tests should cover missing config, unknown directives, `svclib` load failure, provider init failure, CMS library/default paths, standalone role, fspath without stacked FS, trace/debug env, size/time option bounds, and CMS lookup mode.
