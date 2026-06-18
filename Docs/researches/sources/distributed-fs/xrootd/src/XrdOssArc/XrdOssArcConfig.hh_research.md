# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.hh

Purpose: declares the daemon-lifetime configuration object for the archive OSS plug-in.

Important APIs/types/functions: public methods `BuildPath`, `Configure`, `GenTapePath`, constructor/destructor; public fields for helper programs/paths, logical and physical paths, metadata keys, RSEs, backup policy, staging policy, archive naming/size policy, stop monitoring, and local/remote mode; private directive parser helpers.

Control flow: the public API is intentionally broad: other archive modules read config fields directly instead of accessor methods. Private parser methods correspond to `ossarc.*` config directives.

State and persistence behavior: holds process-global configuration and program handles for the lifetime of the plug-in. Many members are `char*` with manual ownership and are initialized in the constructor or parsers.

Dependencies: forward declarations for `XrdOucEnv`, `XrdOucProg`, `XrdOucGatherConf`, and `XrdOssArcStopMon`.

Integration points: global `XrdOssArcGlobals::Config` is used by compose, backup, file, stage, directory, FS monitor, and stop monitor modules.

Risks: public mutable fields allow modules to observe partially initialized state if used before `Configure()` succeeds; destructor intentionally does no cleanup; declared `GenTapePath` is not implemented in the read source, which is a link/maintenance signal unless provided elsewhere.

Test signals: construction default values, successful `Configure()` populates required fields/programs, compile/link check for declared methods, and read-only access by dependent modules after initialization.
