# sources/distributed-fs/xrootd/src/Xrd/XrdStats.hh

## Purpose

`XrdStats.hh` declares the stats aggregation and reporting object used by XRootD server processes. It defines option bitmasks for selecting subsystems and exposes callbacks for on-demand stats delivery. The file was read completely.

## Important APIs, Types, and Functions

Option flags include `XRD_STATS_INFO`, `BUFF`, `LINK`, `POLL`, `PROC`, `PROT`, `SCHD`, `SGEN`, `PLUG`, `ADON`, `SYNC`, `SYNCA`, and `JSON`. Public methods are `Export()`, `Init()`, `Report()`, virtual `Stats()`, and the constructor. Nested abstract `CallBack` supports string and iovec delivery. Private methods generate XML/JSON data and subsystem-specific info/process stats.

## Control Flow

The header models two call paths: scheduled reporting through `Init()`/`Report()` and request-driven reporting through `Stats(CallBack*)`. `GenStats()` is the shared formatter, while `Export()` exposes monitor roll state to plugins via an environment pointer.

## State and Persistence Behavior

State includes UDP destinations, scheduler/log/buffer/monitor pointers, a mutex-protected reusable buffer, formatted header strings, option masks, and server identity metadata. `tBoot` is static boot-time state shared across instances. Destructor frees allocated buffers and header strings.

## Dependencies and Integration Points

Forward declarations keep the header decoupled from `XrdNetMsg`, `XrdMonitor`, scheduler, and buffer manager implementations. It includes `XrdSysPthread.hh` for the stats mutex and `vector` for iovec packet generation.

## Risks and Edge Cases

The virtual `Stats()` exists for packaging/linker reasons, so ABI stability matters. Option bit overlap is intentional: `ALLX` includes XML and JSON-class bits. Consumers must understand that JSON is not supported for client-requested `Stats()` in the implementation.

## Test Signals

Compile and ABI tests should cover plugins that receive `XrdStats` through exported interfaces. Functional tests should check option masks and callback behavior.
