# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPerfMon.hh

Purpose: defines the plugin ABI for CMS performance monitoring. Runtime-loaded libraries inherit `XrdCmsPerfMon` to supply load metrics and optionally receive asynchronous reporting callbacks.

Important APIs/types: virtual `Configure()` receives config filename, directive parameters, logger, CMS monitor callback object, environment, and an `isCMS` flag. `PerfInfo` carries eight one-byte load fields with `Clear()`. `GetInfo()` is polled for metrics; `PutInfo()` reports metrics asynchronously to the CMS monitor.

Control flow: default implementations are no-ops except `Configure()` returns `false`, requiring plugins to override it. Plugin authors expose a file-level `XrdCmsPerfMonitor` pointer and version metadata.

State and persistence: the base class holds no state. `PerfInfo` is transient, with load values expected in the 0-100 range.

Dependencies/integration: forward declares `XrdOucEnv` and `XrdSysLogger`. It integrates with `cms.perf` dynamic loading and CMS scheduler/load reporting.

Risks: ABI stability matters because external plugins compile against this header. Load values are not range-enforced. The documentation says plugin `PutInfo()` will never be called, so implementers must understand directionality.

Test signals: plugin load smoke tests, ABI/version checks, and metric boundary tests for 0, 100, and out-of-range provider behavior.
