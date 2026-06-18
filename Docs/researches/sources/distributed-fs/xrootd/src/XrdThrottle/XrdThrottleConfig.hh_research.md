# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.hh

Purpose: declares the throttle configuration container and parser interface.

Important APIs/types/functions: `Configuration` constructor accepts `XrdSysError` and optional `XrdOucEnv`; `Configure()` populates state; getters expose filesystem library, loadshed host/port/frequency, max open files, max active connections, max wait, throttle concurrency/data/IOPS/recompute interval, trace levels, and per-user config path.

Control flow: users instantiate `Configuration`, call `Configure(config_file)`, then pass it to manager/filesystem code. Private parser methods handle each directive family.

State and persistence: defaults are `libXrdOfs.so`, no loadshed, unlimited max open/connection if `-1`, max wait 30 seconds, no data/IOPS/concurrency throttle if `-1`, recompute interval 1000 ms, trace off, and no user config file.

Dependencies and integration: forward-declares `XrdOucEnv`, `XrdOucStream`, and `XrdSysError`. Consumed by both OSS and OFS throttle setup.

Risks: comments for connection limits use `-1` as unset, while manager's per-user `GetUserMaxConn()` uses `0` to mean global/default; conversions must remain consistent. All getters return raw primitive/string values without validation after parse.

Test signals: default construction, each directive parser via full `Configure()`, and manager `FromConfig()` consumption.
