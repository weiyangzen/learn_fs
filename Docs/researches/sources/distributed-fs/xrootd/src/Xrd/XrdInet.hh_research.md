<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInet.hh

Purpose: declares `XrdInet`, the Xrd-specific network class layered on `XrdNet`.

Important APIs/types/functions: public `Accept`, `BindSD`, `Connect`, `Secure`, constructor/destructor, static `SetAssumeV4`, `GetAssumeV4`, static `netIF`, private `Listen`, `Patrol`, `TraceID`, and static `AssumeV4`.

Control flow: the interface exposes high-level socket lifecycle operations that return `XrdLink` rather than raw fds. Implementation adds security, systemd socket activation, and listen handling.

State and persistence behavior: owns/uses inherited network socket state and a security policy pointer; static flags/interface state affect all instances.

Dependencies: includes `XrdNet/XrdNet.hh` and `XrdNet/XrdNetIF.hh`; forward declares logging, semaphores, security, and link types.

Integration points: server configuration creates one `XrdInet` per bound port; protocol code accepts client links from it; routing and private-address behavior are controlled through static `netIF`.

Risks: static `netIF` and `AssumeV4` are global knobs. `Secure()` accepts a raw pointer and ownership semantics are not obvious from the header. Multiple networks sharing one security object must coordinate lifetime.

Test signals: compile tests for inheritance contract; unit/integration tests through `XrdConfig::getNet()`, `Accept()`, and `Connect()`; global setting tests for `AssumeV4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.hh -->
