# sources/distributed-fs/xrootd/src/Xrd/XrdStats.cc

## Purpose

`XrdStats.cc` implements XRootD runtime statistics generation and automatic UDP reporting. It builds XML reports for server subsystems, optional JSON reports for monitor add-ons and plugins, exports monitor-roll state into `XrdOucEnv`, and schedules periodic reporting through `XrdScheduler`. The file was read completely.

## Important APIs, Types, and Functions

The local `XrdStatsJob` schedules recurring `Report()` calls. The constructor builds XML and JSON header templates with version, source, boot time, program, instance, pid, and site, allocates a page-aligned 64 KiB shared buffer, and creates `XrdMonitor`. `Init()` creates up to two `XrdNetMsg` destinations and enables auto-reporting. `Report()` sends XML and plugin/addon JSON UDP packets. `Stats()` provides callback-based on-demand XML stats. `GenStats()` appends selected subsystem stats. `InfoStats()` and `ProcStats()` format host/port/name and `getrusage()` CPU counters.

## Control Flow

Initialization records destinations and creates a timer job if at least one destination is configured. Each timer firing calls `Report()` and reschedules itself. `Report()` optionally disables synchronous stats collection when `autoSync` is enabled and scheduler activity is high, then locks `statsMutex` around the shared XML buffer. Add-on/plugin JSON packets are generated separately into stack UDP buffers and sent as iovec triplets. On-demand `Stats()` locks the same buffer and invokes callback methods with generated data.

## State and Persistence Behavior

State is process-lifetime memory: destinations, scheduler pointer, buffer manager, monitor object, shared XML buffer, immutable header strings, selected XML/JSON options, auto-sync flag, and host/name/port metadata. There is no persistence beyond emitted network telemetry.

## Dependencies and Integration Points

The implementation integrates with `XrdBuffManager::Stats`, `XrdLink::Stats`, `XrdPoll::Stats`, `XrdProtLoad::Statistics`, `XrdScheduler::Stats`, `XrdMonitor::Format`, `XrdNetMsg::Send`, `XrdSysTimer`, and XRootD version macros. It is a central aggregator for server monitoring.

## Risks and Edge Cases

Report generation assumes a 64 KiB UDP-sized buffer; long plugin/addon output may be truncated by `Format()` behavior. `GenStats(std::vector<iovec>&)` duplicates stack-built packet strings but the caller must free those `iov_base` allocations. XML generation uses `snprintf` return lengths without deeply checking available space after each subsystem. `autoSync` trades consistency for lower scheduler pressure when activity exceeds 30. If `posix_memalign()` fails, `GenStats()` returns a minimal null stats document.

## Test Signals

Tests should validate XML fragments for every option bit, JSON plugin/addon packet framing, dual-destination reporting, callback output, behavior with null buffer allocation, large plugin output, and auto-sync behavior under high scheduler activity.
