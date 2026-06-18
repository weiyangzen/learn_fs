# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsMeter.cc

Purpose: implements the global CMS load/space meter. It monitors local filesystem capacity, consumes external or plugin performance metrics, computes weighted load, and reports usage/space changes to managers.

Important APIs/types/functions: global `XrdCms::Meter`, `XrdCmsMeter::{Init,Monitor,Run,RunFS,RunPM,PutInfo,Update,Record,Report,FreeSpace,TotalSpace,calcLoad,calcSpace,SpaceMsg,UpdtSpace}`.

Control flow: construction sets all counters to neutral values. `Init()` reads initial `XrdOssVSInfo`, computes minimum/high-water free thresholds from config, calls `calcSpace()`, updates `CmsState::Space`, starts an FS meter thread, and logs capacity. `Monitor(char*,int)` validates and starts an external program, while `Monitor(int)` loads/configures a perfmon plugin and optionally starts a polling thread. `Run()` repeatedly execs the external program and parses metric lines through `Update()`. `RunFS()` sleeps at `dsk_calc` intervals, recalculates space, toggles no-space state based on min/high-water hysteresis, and sends state updates. `PutInfo()` and `Update()` clamp/parse metrics, compute weighted load, and trigger `XrdCmsNode::Report_Usage(0)` when load changes exceed fuzz. `FreeSpace()` and `TotalSpace()` return physical or virtual cluster-space values.

State and persistence behavior: in-memory current metrics, disk totals/free/utilization, threshold displays, monitor process/thread state, virtual filesystem cache, and reporting timestamps. No durable persistence, but it drives cluster-visible state.

Dependencies: `XrdCmsConfig`, `XrdCmsCluster`, `XrdCmsState`, `XrdCmsNode`, `XrdCmsUtils`, `XrdOss`, `XrdOucStream`, thread/timer/platform APIs, and perfmon plugin interface.

Integration points: `XrdCmsNode::do_Load()`, `do_Space()`, and `Report_Usage()` call into the meter. Cluster managers use these reports for selection and staging decisions. Perfmon plugins can call `PutInfo()`.

Risks: `Monitor(int)` declares a local `monPerf` that shadows the member and then `RunPM()` uses the member, which appears to leave the member null in this source and would crash if the polling thread runs. The condition `if (monint)` likely intended `if (itv)`, so plugin polling may not start as expected. External monitor output must be exactly five unsigned values. The destructor kills only the monitor thread, not the FS thread. Disk totals are cached initially and may be stale if filesystems are added/removed.

Test signals: threshold/hysteresis tests for min/high-water transitions, mocked `StatVS()` failures and zero-total retries, external monitor parse tests, plugin monitor polling tests that catch the shadowing bug, virtual FS update tests, load fuzz alert tests, and thread cleanup/leak checks.
