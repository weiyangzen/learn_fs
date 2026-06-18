## sources/distributed-fs/xrootd/src/Xrd/XrdProtocol.hh

Purpose: defines the abstract protocol interface and configuration structure used by XRootD core to load, configure, match, run, recycle, and report protocol implementations.

Important APIs/types/functions: `XrdProtocol_Config` passes stable services (`eDest`, `NetTCP`, `BPool`, `Sched`, `Stats`, `theEnv`, `tlsCtx`, `totalCF`) and unstable configuration values that protocols must copy if retained. `XrdProtocol` derives from `XrdJob` and requires `Match(XrdLink*)`, `Process(XrdLink*)`, `Recycle(XrdLink*, int, const char*)`, and `Stats(char*, int, int)`. Comments define required `extern "C"` plugin entry points `XrdgetProtocol` and `XrdgetProtocolPort`.

Control flow: configuration creates a protocol object via the entry point. For each accepted link, the loader calls `Match()`; poll events call `Process()`; close calls `Recycle()`; report paths call `Stats()`.

State/persistence: the config object is transient except for documented stable pointers. Protocol implementations own their own persistent runtime state.

Dependencies/integration: includes `XrdJob` and forward-declares core services, network address types, scheduler, stats, TLS context, and environment objects.

Risks: the copy constructor is deleted to prevent accidental whole-object retention, but protocols can still store unstable pointers manually. ABI compatibility matters for shared-library plugins. `Stats()` snprintf semantics are part of the contract and must be honored for aggregation.

Test signals: plugin tests should verify port discovery, protocol construction, match failure/success, process return-code semantics with `XrdLinkXeq::DoIt()`, recycle reason propagation, and stats sizing with null buffer.
