# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.hh

Purpose: declares `XrdCmsMeter`, the CMS performance and filesystem-space monitor, and the global `XrdCms::Meter` instance.

Important APIs/types/functions: load calculators, `FreeSpace()`, `TotalSpace()`, `Init()`, `Monitor()` overloads, `PutInfo()`, `Record()`, `Report()`, `Run()`/`RunFS()`/`RunPM()`, virtual filesystem controls `setVirtual()`/`setVirtUpdt()`, and private helpers for space calculation and display scaling.

Control flow: callers initialize disk monitoring, optionally start an external or plugin perf monitor, then query/report current load and space through the public API. Background threads use the `Run*` methods.

State and persistence behavior: stores current disk and load metrics, thresholds, monitor program/plugin state, mutexes, virtual FS flags, and thread id. All state is volatile daemon memory.

Dependencies: `XrdCmsPerfMon`, `XrdSysError`, pthread mutexes, and `XrdOucStream`.

Integration points: global meter is used by node command handlers and cluster state reporting. It also implements `XrdCmsPerfMon` so plugins can feed performance data.

Risks: many fields are manually synchronized with `cfsMutex` and `repMutex`; callers must avoid lock inversions. The class assumes singleton lifetime. Virtual FS state changes require `setVirtUpdt()` to refresh cached cluster space.

Test signals: API compile tests, concurrent `Report()`/`PutInfo()`/`FreeSpace()` stress, virtual FS mode behavior, and monitor lifecycle tests.
