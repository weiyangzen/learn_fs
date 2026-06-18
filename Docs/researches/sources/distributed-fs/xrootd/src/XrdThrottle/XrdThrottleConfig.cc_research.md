# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.cc

Purpose: parses throttle configuration directives from the XRootD config file into a `Configuration` object.

Important APIs/types/functions: `Configuration::Configure()`, parsers `xmaxopen()`, `xmaxconn()`, `xmaxwait()`, `xthrottle()`, `xloadshed()`, `xtrace()`, and `xuserconfig()`. The `TS_Xeq` macro dispatches recognized directive names.

Control flow: `Configure()` opens the config file, attaches it to `XrdOucStream`, captures throttle plugin config lines, then loops over directive names. `throttle.fslib` is handled inline; other known directives call parser methods. Numeric values are parsed with `XrdOuca2x`. `xthrottle()` scans option pairs for data rate, IOPS rate, recompute interval, and concurrency. `xloadshed()` requires a host and parses optional port/frequency. `xtrace()` accumulates trace flags with support for negation and off/none.

State and persistence: parsed settings persist in `Configuration` members until consumed by `XrdThrottleManager::FromConfig()` or filesystem loading. It does not write files or mutate global runtime state.

Dependencies and integration: depends on `XrdOucStream`, `XrdOuca2x`, `XrdOucEnv`, `XrdSysError`, trace constants, and config syntax used by both OSS and OFS throttle wrappers.

Risks: parser functions log missing mandatory values but do not always immediately return after the log before using `val`, which can lead to null handling issues. `TS_Xeq` resets `NoGo` to zero for every nonmatching directive, so unknown directives are ignored by this plugin. `xloadshed()` defaults port/frequency to zero even though comments mention defaults; loadshed is applied only when all three are positive later.

Test signals: parse complete config, missing values, bad numeric ranges, trace flag accumulation/negation, unknown options, user config path, and fslib override.
